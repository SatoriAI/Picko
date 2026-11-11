import json
import sys
from types import SimpleNamespace

import httpx
import pytest
from sqlalchemy import text

from source.database.connection import ENGINE
from source.settings import LanguageSelection
from source.tasks.draw import draw_and_notify
from source.utils.postman import PostMan, PostManSendError
from tests.support import close_registration, create_event_with_participants, fetch_all, register

# `source.tasks` re-exports the task under the module's own name, so the module is only reachable this way.
DRAW_TASK_MODULE = sys.modules["source.tasks.draw"]


class FakeResend:
    """Stands in for the Resend API: records each accepted recipient and rejects the ones it is told to."""

    def __init__(self) -> None:
        self.rejected: set[str] = set()
        self.delivered: list[dict] = []
        self.handler = self.handle

    def handle(self, request: httpx.Request) -> httpx.Response:
        payload = json.loads(request.content)
        if payload["to"][0] in self.rejected:
            return httpx.Response(httpx.codes.UNPROCESSABLE_ENTITY, json={"message": "rejected"})
        self.delivered.append(payload)
        return httpx.Response(httpx.codes.OK, json={"id": f"email-{len(self.delivered)}"})

    @property
    def recipients(self) -> list[str]:
        return [payload["to"][0] for payload in self.delivered]

    def postman(self) -> PostMan:
        return PostMan(client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))


@pytest.fixture
def resend(monkeypatch) -> FakeResend:
    fake = FakeResend()
    monkeypatch.setattr(DRAW_TASK_MODULE, "PostMan", fake.postman)
    return fake


async def test_the_join_link_points_at_the_frontend_even_with_several_cors_origins(resend):
    participant = SimpleNamespace(
        email="ann@example.com",
        name="Ann",
        language=LanguageSelection.EN,
        given_assignments=[SimpleNamespace(reveal_token="TOKEN")],
    )

    async with resend.postman() as postman:
        await postman.send_assignment_email(participant, event_id=1)

    assert resend.delivered[0]["text"] == "https://picko.test/join/TOKEN"
    assert 'href="https://picko.test/join/TOKEN"' in resend.delivered[0]["html"]


async def test_a_failed_send_is_reported_and_not_swallowed(resend):
    resend.rejected = {"ann@example.com"}
    participant = SimpleNamespace(
        email="ann@example.com",
        name="Ann",
        language=LanguageSelection.EN,
        given_assignments=[SimpleNamespace(reveal_token="TOKEN")],
    )

    async with resend.postman() as postman:
        with pytest.raises(PostManSendError):
            await postman.send_assignment_email(participant, event_id=1)


async def test_a_rerun_emails_only_the_participants_whose_send_failed(client, resend):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Cid"])
    await register(client, event["registration_token"], "NoEmail")
    await close_registration(event["id"])

    resend.rejected = {"bob@example.com"}
    first = await draw_and_notify(event["id"])

    assert (first["sent"], first["failed"]) == (2, 1)
    assert sorted(resend.recipients) == ["ann@example.com", "cid@example.com"]
    assert (await fetch_all("SELECT notified_at FROM event"))[0].notified_at is None
    notified = await fetch_all("SELECT name FROM participant WHERE notified_at IS NOT NULL ORDER BY name")
    assert [row.name for row in notified] == ["Ann", "Cid"]

    resend.rejected = set()
    resend.delivered.clear()
    second = await draw_and_notify(event["id"])

    assert (second["sent"], second["failed"]) == (1, 0)
    assert resend.recipients == ["bob@example.com"]
    assert (await fetch_all("SELECT notified_at FROM event"))[0].notified_at is not None

    resend.delivered.clear()
    third = await draw_and_notify(event["id"])

    assert third["status"] == "already_notified"
    assert resend.delivered == []
    assert len(await fetch_all("SELECT id FROM draw")) == 1


async def test_an_address_added_while_emails_go_out_is_emailed_before_the_event_closes(client, resend):
    event = await create_event_with_participants(client, ["Ann", "Bob"])
    await register(client, event["registration_token"], "Late")
    await close_registration(event["id"])

    async def add_an_address_during_the_first_send(request: httpx.Request) -> httpx.Response:
        if not resend.delivered:
            async with ENGINE.begin() as connection:
                await connection.execute(text("UPDATE participant SET email = 'late@example.com' WHERE name = 'Late'"))
        return resend.handle(request)

    resend.handler = add_an_address_during_the_first_send
    result = await draw_and_notify(event["id"])

    assert result["status"] == "emails_sent"
    assert sorted(resend.recipients) == ["ann@example.com", "bob@example.com", "late@example.com"]
    assert (await fetch_all("SELECT notified_at FROM event"))[0].notified_at is not None
