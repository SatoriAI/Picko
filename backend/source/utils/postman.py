from dataclasses import dataclass
import html as html_lib
from functools import lru_cache
from pathlib import Path
from string import Template
from typing import Any, Optional, Sequence, Union

from anyio import to_thread
from fastapi import Request, status
from structlog import get_logger

import requests

logger = get_logger()


class PostManError(RuntimeError):
    pass


class PostManConfigError(PostManError):
    pass


class PostManSendError(PostManError):
    pass


@dataclass(frozen=True)
class SendResult:
    id: str
    raw: dict[str, Any]


class PostMan:
    BASE_URL = "https://api.resend.com/emails"

    def __init__(
        self,
        settings: Any,
        *,
        timeout: float = 20.0,
        session: requests.Session | None = None,
    ) -> None:
        self._sender = getattr(settings, "email_from", None)
        self._api_key = getattr(settings, "resend_api_key", None)

        if not self._sender or not isinstance(self._sender, str):
            raise PostManConfigError("Missing/invalid settings.email_from")
        if not self._api_key or not isinstance(self._api_key, str):
            raise PostManConfigError("Missing/invalid settings.resend_api_key")

        self._timeout = timeout
        self._session = session or requests.Session()

    @staticmethod
    def _pick_frontend_origin(
        *, request: Request, cors_origins: str | None = None
    ) -> str:
        """
        Best-effort frontend origin detection for building the /join/{token} link:
        - Prefer the incoming request Origin header (frontend calling the API).
        - Fallback to provided cors_origins (often configured as a single origin).
        - As a last resort use backend base_url.
        """
        origin = (request.headers.get("origin") or "").strip()
        if origin and origin.lower() != "null":
            return origin.rstrip("/")

        cors = (cors_origins or "").strip()
        if cors:
            # Support common "a,b,c" style values even though the app currently
            # passes the whole string as a single origin entry.
            first = next((p.strip() for p in cors.split(",") if p.strip()), "")
            if first and first != "*":
                return first.rstrip("/")

        return str(request.base_url).rstrip("/")

    @staticmethod
    def _normalize_language(language: str | None) -> str:
        lang = (language or "en").strip().lower()
        return "pl" if lang.startswith("pl") else "en"

    @staticmethod
    @lru_cache(maxsize=8)
    def _load_christmas_template(language: str) -> str:
        lang = PostMan._normalize_language(language)
        template_path = (
            Path(__file__).resolve().parent / "templates" / "christmas" / f"{lang}.html"
        )
        return template_path.read_text(encoding="utf-8")

    @staticmethod
    def _render_christmas_email_html(
        *,
        language: str | None,
        join_url: str,
        app_name: str = "Picko",
    ) -> str:
        raw = PostMan._load_christmas_template(PostMan._normalize_language(language))
        return Template(raw).safe_substitute(
            join_url=html_lib.escape(join_url),
            app_name=html_lib.escape(app_name),
        )

    @staticmethod
    def _render_christmas_email_text(
        *,
        language: str | None,
        join_url: str,
        app_name: str = "Picko",
    ) -> str:
        # Requirement: email should contain only the link (no receiver details).
        # Keep the plain-text version literally as the URL.
        _ = (language, app_name)  # reserved for future localization/branding
        return join_url.strip()

    @staticmethod
    def _normalize_recipients(value: Union[str, Sequence[str]]) -> list[str]:
        if isinstance(value, str):
            value = [value]

        if not (
            recipients := [v.strip() for v in value if isinstance(v, str) and v.strip()]
        ):
            raise ValueError("Recipient list is empty.")
        return recipients

    def send(
        self,
        *,
        to: Union[str, Sequence[str]],
        subject: str,
        text: Optional[str] = None,
        html: Optional[str] = None,
        cc: Optional[Union[str, Sequence[str]]] = None,
        bcc: Optional[Union[str, Sequence[str]]] = None,
        reply_to: Optional[str] = None,
        tags: Optional[dict[str, str]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> SendResult:
        if not subject or not subject.strip():
            raise ValueError("subject is required")

        if (text is None or not text.strip()) and (
            html is None or not str(html).strip()
        ):
            raise ValueError("Provide at least one of: text or html")

        payload: dict[str, Any] = {
            "from": self._sender,
            "to": self._normalize_recipients(to),
            "subject": subject.strip(),
        }

        if text and text.strip():
            payload["text"] = text
        if html and str(html).strip():
            payload["html"] = html

        if cc is not None:
            payload["cc"] = self._normalize_recipients(cc)
        if bcc is not None:
            payload["bcc"] = self._normalize_recipients(bcc)
        if reply_to and reply_to.strip():
            payload["reply_to"] = reply_to.strip()

        if tags:
            payload["tags"] = [{"name": k, "value": v} for k, v in tags.items()]

        if headers:
            payload["headers"] = headers

        try:
            resp = self._session.post(
                self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self._timeout,
            )
        except requests.RequestException as e:
            raise PostManSendError(f"Network error sending email: {e}") from e

        try:
            data = resp.json()
        except ValueError:
            data = {"raw_text": resp.text}

        if resp.status_code >= status.HTTP_400_BAD_REQUEST:
            raise PostManSendError(f"Resend error {resp.status_code}: {data}")

        msg_id = data.get("id")
        if not msg_id:
            raise PostManSendError(f"Resend returned success but no id: {data}")

        return SendResult(id=msg_id, raw=data)

    async def send_event_emails(
        self,
        *,
        participants: Sequence[Any],
        event_id: int,
        request: Request,
        cors_origins: str | None = None,
        app_name: str = "Picko",
    ) -> tuple[list[str], int]:
        """
        Sends Secret Santa assignment emails for a whole event.

        Expected participant shape (duck-typed):
        - participant.email: str | None
        - participant.name: str
        - participant.language: str
        - participant.given_assignments: list with [0].reveal_token
        - participant.event: (used only for tagging/logging)
        """
        sent_to: list[str] = []
        skipped_count = 0

        frontend_origin = self._pick_frontend_origin(
            request=request, cors_origins=cors_origins
        )

        try:
            for participant in participants:
                if not getattr(participant, "email", None):
                    skipped_count += 1
                    continue

                given_assignments = (
                    getattr(participant, "given_assignments", None) or []
                )
                if not given_assignments:
                    skipped_count += 1
                    continue

                assignment = given_assignments[0]
                event = getattr(participant, "event", None)
                if event is None:
                    skipped_count += 1
                    continue

                join_url = f"{frontend_origin}/join/{assignment.reveal_token}"
                language = self._normalize_language(
                    getattr(participant, "language", "en")
                )
                subject = (
                    "Secret Santa: your reveal link 🎄"
                    if language == "en"
                    else "Secret Santa: Twój link do odkrycia 🎄"
                )

                html_body = self._render_christmas_email_html(
                    language=language,
                    join_url=join_url,
                    app_name=app_name,
                )
                text_body = self._render_christmas_email_text(
                    language=language,
                    join_url=join_url,
                    app_name=app_name,
                )

                try:
                    result = await to_thread.run_sync(
                        lambda: self.send(
                            to=participant.email,
                            subject=subject,
                            html=html_body,
                            text=text_body,
                            tags={"event_id": str(event_id)},
                        )
                    )
                except PostManSendError as exc:
                    logger.exception(
                        "Failed to send email",
                        to=participant.email,
                        participant_name=participant.name,
                        event_id=event_id,
                        error=str(exc),
                    )
                    skipped_count += 1
                    continue

                logger.info(
                    "Email sent",
                    to=participant.email,
                    participant_name=participant.name,
                    event_id=event_id,
                    resend_id=result.id,
                )
                sent_to.append(participant.name)
        finally:
            # Make sure we always close the underlying session.
            self.close()

        return sent_to, skipped_count

    def close(self) -> None:
        self._session.close()
