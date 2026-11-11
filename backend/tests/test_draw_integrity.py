import asyncio

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from source.database.connection import ENGINE
from tests.support import close_registration, create_event, create_event_with_participants, fetch_all, register


async def test_concurrent_requests_after_the_deadline_create_one_draw(client):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Cid", "Dee"])
    await close_registration(event["id"])

    responses = await asyncio.gather(*[client.get(f"/event/{event['id']}") for _ in range(8)])

    assert {response.status_code for response in responses} == {httpx.codes.OK}
    assert len(await fetch_all("SELECT id FROM draw")) == 1
    per_giver = await fetch_all("SELECT giver_id, count(*) AS total FROM assignment GROUP BY giver_id")
    assert len(per_giver) == 4
    assert {row.total for row in per_giver} == {1}


async def test_concurrent_participant_pages_after_the_deadline_create_one_draw(client):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Cid"])
    access_tokens = [row.access_token for row in await fetch_all("SELECT access_token FROM participant")]
    await close_registration(event["id"])

    responses = await asyncio.gather(*[client.get(f"/participant/me/{token}") for token in access_tokens * 3])

    assert len(await fetch_all("SELECT id FROM draw")) == 1
    assert all(response.json()["assignment"] is not None for response in responses)


async def test_the_schema_refuses_a_second_draw_for_an_event(client):
    event = await create_event(client)

    async with ENGINE.begin() as connection:
        await connection.execute(text("INSERT INTO draw (event_id) VALUES (:id)"), {"id": event["id"]})

    with pytest.raises(IntegrityError):
        async with ENGINE.begin() as connection:
            await connection.execute(text("INSERT INTO draw (event_id) VALUES (:id)"), {"id": event["id"]})


async def test_registration_waits_for_a_draw_in_progress_and_is_then_rejected(client):
    event = await create_event_with_participants(client, ["Ann", "Bob"])

    async with ENGINE.connect() as draw_in_progress:
        # Hold the row lock the draw takes, as if the draw were between reading participants and committing.
        await draw_in_progress.execute(text("SELECT id FROM event WHERE id = :id FOR UPDATE"), {"id": event["id"]})

        registration = asyncio.create_task(register(client, event["registration_token"], "Late"))
        done, _ = await asyncio.wait({registration}, timeout=0.5)
        assert not done, "registration finished while the draw held the event"

        await draw_in_progress.execute(
            text("UPDATE event SET is_draw_complete = true WHERE id = :id"), {"id": event["id"]}
        )
        await draw_in_progress.commit()

    response = await registration
    assert response.status_code == httpx.codes.BAD_REQUEST
    assert [row.name for row in await fetch_all("SELECT name FROM participant ORDER BY id")] == ["Ann", "Bob"]
