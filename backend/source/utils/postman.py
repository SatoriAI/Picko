from dataclasses import dataclass
import datetime
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
    @lru_cache(maxsize=1)
    def _load_christmas_template() -> str:
        template_path = Path(__file__).resolve().parent / "templates" / "christmas.html"
        return template_path.read_text(encoding="utf-8")

    @staticmethod
    def _render_christmas_email_html(
        *,
        participant_name: str,
        receiver_name: str,
        event_name: str,
        event_date: datetime.date | None,
        max_amount: int | None,
        currency: str | None,
        join_url: str,
        app_name: str = "Picko",
    ) -> str:
        event_date_html = ""
        if event_date is not None:
            event_date_html = (
                f'<p style="margin: 0; color: #334155;"><strong>Date:</strong> '
                f"{html_lib.escape(event_date.strftime('%d %b %Y'))}</p>"
            )

        budget_html = ""
        if max_amount is not None:
            budget_html = (
                f'<p style="margin: 8px 0 0; color: #334155;"><strong>Budget:</strong> '
                f"{html_lib.escape(str(max_amount))} "
                f"{html_lib.escape(currency or 'PLN')}</p>"
            )

        raw = PostMan._load_christmas_template()
        return Template(raw).safe_substitute(
            participant_name=html_lib.escape(participant_name),
            receiver_name=html_lib.escape(receiver_name),
            event_name=html_lib.escape(event_name),
            join_url=html_lib.escape(join_url),
            event_date_html=event_date_html,
            budget_html=budget_html,
            app_name=html_lib.escape(app_name),
        )

    @staticmethod
    def _render_christmas_email_text(
        *,
        participant_name: str,
        receiver_name: str,
        event_name: str,
        event_date: datetime.date | None,
        max_amount: int | None,
        currency: str | None,
        join_url: str,
        app_name: str = "Picko",
    ) -> str:
        lines: list[str] = [
            f"Ho ho ho, {participant_name}!",
            "",
            f"Your Secret Santa assignment for '{event_name}' is ready.",
            f"You are gifting: {receiver_name}",
        ]

        if event_date is not None:
            lines.append(f"Date: {event_date.strftime('%d %b %Y')}")
        if max_amount is not None:
            lines.append(f"Budget: {max_amount} {currency or 'PLN'}")

        lines += [
            "",
            "Open your gift (keep it secret!):",
            join_url,
            "",
            "Merry Christmas!",
            f"— Santa (via {app_name})",
        ]
        return "\n".join(lines)

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
        - participant.given_assignments: list with [0].reveal_token and [0].receiver.name
        - participant.event: has name/date/max_amount/currency
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

                receiver = getattr(assignment, "receiver", None)
                receiver_name = getattr(receiver, "name", None) or ""

                join_url = f"{frontend_origin}/join/{assignment.reveal_token}"
                subject = (
                    f"Ho ho ho! Your Secret Santa match for {event.name} is ready 🎄"
                )

                html_body = self._render_christmas_email_html(
                    participant_name=participant.name,
                    receiver_name=receiver_name,
                    event_name=event.name,
                    event_date=getattr(event, "date", None),
                    max_amount=getattr(event, "max_amount", None),
                    currency=getattr(event, "currency", None),
                    join_url=join_url,
                    app_name=app_name,
                )
                text_body = self._render_christmas_email_text(
                    participant_name=participant.name,
                    receiver_name=receiver_name,
                    event_name=event.name,
                    event_date=getattr(event, "date", None),
                    max_amount=getattr(event, "max_amount", None),
                    currency=getattr(event, "currency", None),
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
