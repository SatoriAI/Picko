from dataclasses import dataclass
from typing import Any, Optional, Sequence, Union

from fastapi import status

import requests


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
        self._sender = getattr(settings, "sender", None)
        self._api_key = getattr(settings, "resend_api_key", None)

        if not self._sender or not isinstance(self._sender, str):
            raise PostManConfigError("Missing/invalid settings.sender")
        if not self._api_key or not isinstance(self._api_key, str):
            raise PostManConfigError("Missing/invalid settings.resend_api_key")

        self._timeout = timeout
        self._session = session or requests.Session()

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

    def close(self) -> None:
        self._session.close()
