import html as html_lib
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache, partial
from pathlib import Path
from string import Template
from typing import Any

import requests
from anyio import to_thread
from fastapi import Request, status
from structlog import get_logger

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

    def __init__(self, settings: Any, *, timeout: float = 20.0, session: requests.Session | None = None) -> None:
        self._sender = getattr(settings, "email_from", None)
        self._api_key = getattr(settings, "resend_api_key", None)
        self._frontend_origin = getattr(settings, "cors_origins", None)
        self._app_name = getattr(settings, "app_name", None)

        if not self._sender:
            raise PostManConfigError("Missing settings.email_from!")
        if not self._api_key:
            raise PostManConfigError("Missing settings.resend_api_key!")
        if not self._frontend_origin:
            raise PostManConfigError("Missing settings.cors_origins!")
        if not self._app_name:
            raise PostManConfigError("Missing settings.app_name!")

        self._timeout = timeout
        self._session = session or requests.Session()

    @staticmethod
    def _normalize_language(language: str | None) -> str:
        return "pl" if (language or "en").strip().lower().startswith("pl") else "en"

    @staticmethod
    @lru_cache(maxsize=8)
    def _load_christmas_template(language: str) -> str:
        lang = PostMan._normalize_language(language)
        path = Path(__file__).resolve().parent / "templates" / "christmas" / f"{lang}.html"
        return path.read_text(encoding="utf-8")

    @staticmethod
    def _render_christmas_email_html(*, language: str | None, join_url: str, app_name: str = "Picko") -> str:
        return Template(PostMan._load_christmas_template(language or "en")).safe_substitute(
            join_url=html_lib.escape(join_url),
            app_name=html_lib.escape(app_name),
        )

    @staticmethod
    def _render_christmas_email_text(*, join_url: str, **_: Any) -> str:
        return join_url.strip()

    @staticmethod
    def _normalize_recipients(value: str | Sequence[str]) -> list[str]:
        values = [value] if isinstance(value, str) else value
        recipients = [v.strip() for v in values if isinstance(v, str) and v.strip()]
        if not recipients:
            raise ValueError("Recipient list is empty.")
        return recipients

    def send(
        self,
        *,
        to: str | Sequence[str],
        subject: str,
        text: str | None = None,
        html: str | None = None,
        cc: str | Sequence[str] | None = None,
        bcc: str | Sequence[str] | None = None,
        reply_to: str | None = None,
        tags: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
    ) -> SendResult:
        if not (subject := (subject or "").strip()):
            raise ValueError("subject is required")

        text_s, html_s = (text or "").strip(), (html or "").strip()
        if not (text_s or html_s):
            raise ValueError("Provide at least one of: text or html")

        payload: dict[str, Any] = {
            "from": self._sender,
            "to": self._normalize_recipients(to),
            "subject": subject,
        }
        if text_s:
            payload["text"] = text_s
        if html_s:
            payload["html"] = html_s
        if cc is not None:
            payload["cc"] = self._normalize_recipients(cc)
        if bcc is not None:
            payload["bcc"] = self._normalize_recipients(bcc)
        if reply_to and (reply_to := reply_to.strip()):
            payload["reply_to"] = reply_to
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

        if not (msg_id := data.get("id")):
            raise PostManSendError(f"Resend returned success but no id: {data}")

        return SendResult(id=msg_id, raw=data)

    async def send_event_emails(
        self, *, participants: Sequence[Any], event_id: int, request: Request
    ) -> tuple[list[str], int]:
        _ = request  # keep signature; not used in current behavior

        sent_to: list[str] = []
        skipped = 0

        try:
            for p in participants:
                if not getattr(p, "email", None):
                    skipped += 1
                    continue

                assignments = getattr(p, "given_assignments", None) or []
                if not assignments or not getattr(p, "event", None):
                    skipped += 1
                    continue

                token = assignments[0].reveal_token
                join_url = f"{self._frontend_origin}/join/{token}"

                lang = self._normalize_language(getattr(p, "language", "en"))
                subject = (
                    "Secret Santa: your reveal link 🎄" if lang == "en" else "Secret Santa: Twój link do odkrycia 🎄"
                )

                html_body = self._render_christmas_email_html(language=lang, join_url=join_url, app_name=self._app_name)
                text_body = self._render_christmas_email_text(language=lang, join_url=join_url, app_name=self._app_name)

                try:
                    result = await to_thread.run_sync(
                        partial(
                            self.send,
                            to=p.email,
                            subject=subject,
                            html=html_body,
                            text=text_body,
                            tags={"event_id": str(event_id)},
                        )
                    )
                except PostManSendError as exc:
                    logger.exception(
                        "Failed to send email",
                        to=p.email,
                        participant_name=getattr(p, "name", None),
                        event_id=event_id,
                        error=str(exc),
                    )
                    skipped += 1
                    continue

                logger.info(
                    "Email sent",
                    to=p.email,
                    participant_name=getattr(p, "name", None),
                    event_id=event_id,
                    resend_id=result.id,
                )
                sent_to.append(getattr(p, "name", ""))

        finally:
            self.close()

        return sent_to, skipped

    def close(self) -> None:
        self._session.close()
