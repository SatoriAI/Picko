import html as html_lib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from string import Template
from typing import Any, Protocol

import httpx
from fastapi import status
from structlog import get_logger

from source.settings import LanguageSelection, Settings, settings

logger = get_logger()


class PostManError(RuntimeError):
    pass


class PostManSendError(PostManError):
    pass


@dataclass(frozen=True)
class SendResult:
    id: str
    raw: dict[str, Any]


class AssignmentProtocol(Protocol):
    reveal_token: str


class ParticipantProtocol(Protocol):
    email: str | None
    name: str | None
    language: LanguageSelection
    event: Any
    given_assignments: Sequence[AssignmentProtocol]


class PostMan:
    BASE_URL = "https://api.resend.com/emails"

    def __init__(
        self, settings: Settings = settings, *, timeout: float = 20.0, client: httpx.AsyncClient | None = None
    ) -> None:
        self._sender = settings.email_from
        self._api_key = settings.resend_api_key
        self._frontend_origin = settings.cors_origins
        self._app_name = settings.app_name

        self._timeout = timeout
        self._client = client
        self._owns_client = client is None

    async def __aenter__(self) -> "PostMan":
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    @staticmethod
    @lru_cache(maxsize=8)
    def _load_christmas_template(language: LanguageSelection) -> str:
        path = Path(__file__).resolve().parent / "templates" / "christmas" / f"{language}.html"
        return path.read_text(encoding="utf-8")

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_christmas_subjects() -> dict[str, str]:
        path = Path(__file__).resolve().parent / "templates" / "christmas" / "subject.json"
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _get_christmas_subject(language: LanguageSelection) -> str:
        subjects = PostMan._load_christmas_subjects()
        return subjects[language.value]

    @staticmethod
    def _render_christmas_email_html(*, language: LanguageSelection, join_url: str, app_name: str = "Picko") -> str:
        return Template(PostMan._load_christmas_template(language)).safe_substitute(
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

    async def send(
        self,
        *,
        to: str | Sequence[str],
        subject: str,
        text: str | None = None,
        html: str | None = None,
        tags: dict[str, str] | None = None,
    ) -> SendResult:
        subject = (subject or "").strip()
        if not subject:
            raise ValueError("subject is required")

        text_body = (text or "").strip()
        html_body = (html or "").strip()
        if not (text_body or html_body):
            raise ValueError("Provide at least one of: text or html")

        payload: dict[str, Any] = {
            "from": self._sender,
            "to": self._normalize_recipients(to),
            "subject": subject,
        }
        if text_body:
            payload["text"] = text_body
        if html_body:
            payload["html"] = html_body
        if tags:
            payload["tags"] = [{"name": k, "value": v} for k, v in tags.items()]

        if self._client is None:
            raise PostManSendError("PostMan client not initialized. Use 'async with PostMan() as postman:'")

        try:
            resp = await self._client.post(
                self.BASE_URL,
                headers={"Authorization": f"Bearer {self._api_key}"},
                json=payload,
            )
        except httpx.RequestError as e:
            raise PostManSendError(f"Network error sending email: {e}") from e

        try:
            data = resp.json()
        except ValueError:
            data = {"raw_text": resp.text}

        if resp.status_code >= status.HTTP_400_BAD_REQUEST:
            # Sanitize response to avoid leaking sensitive info
            safe_data = {k: v for k, v in data.items() if k not in ("request", "headers")}
            raise PostManSendError(f"Resend error {resp.status_code}: {safe_data}")

        msg_id = data.get("id")
        if not msg_id:
            raise PostManSendError(f"Resend returned success but no id: {data}")

        return SendResult(id=msg_id, raw=data)

    async def send_event_emails(
        self, *, participants: Sequence[ParticipantProtocol], event_id: int
    ) -> tuple[list[str], int]:
        sent_to: list[str] = []
        skipped = 0

        for participant in participants:
            if not participant.email:
                skipped += 1
                continue

            assignments = participant.given_assignments
            if not assignments or not participant.event:
                skipped += 1
                continue

            token = assignments[0].reveal_token
            join_url = f"{self._frontend_origin}/join/{token}"

            lang = participant.language
            subject = self._get_christmas_subject(lang)

            html_body = self._render_christmas_email_html(language=lang, join_url=join_url, app_name=self._app_name)
            text_body = self._render_christmas_email_text(language=lang, join_url=join_url, app_name=self._app_name)

            try:
                result = await self.send(
                    to=participant.email,
                    subject=subject,
                    html=html_body,
                    text=text_body,
                    tags={"event_id": str(event_id)},
                )
            except PostManSendError as exc:
                logger.exception(
                    "Failed to send email",
                    to=participant.email,
                    participant_name=participant.name,
                    event_id=event_id,
                    error=str(exc),
                )
                skipped += 1
                continue

            logger.info(
                "Email sent",
                to=participant.email,
                participant_name=participant.name,
                event_id=event_id,
                resend_id=result.id,
            )
            sent_to.append(participant.name or "")

        return sent_to, skipped

    async def close(self) -> None:
        if self._client and self._owns_client:
            await self._client.aclose()
            self._client = None
