import asyncio

import httpx
import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from source.database.connection import ENGINE, AsyncSessionLocal
from source.database.operations import execute_draw_if_due
from source.endpoints import participant as participant_page
from tests.support import (
    close_registration,
    create_event,
    create_event_with_participants,
    fetch_all,
    register,
    wait_until_a_query_waits_on_a_lock,
)


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


async def test_a_request_waits_for_a_draw_in_progress_instead_of_starting_its_own(client):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Cid"])
    await close_registration(event["id"])
    participant_ids = [row.id for row in await fetch_all("SELECT id FROM participant ORDER BY id")]

    async with ENGINE.connect() as other_draw:
        await other_draw.execute(text("SELECT id FROM event WHERE id = :id FOR UPDATE"), {"id": event["id"]})

        request = asyncio.create_task(client.get(f"/event/{event['id']}"))
        await wait_until_a_query_waits_on_a_lock()

        draw_id = (
            await other_draw.execute(text("INSERT INTO draw (event_id) VALUES (:id) RETURNING id"), {"id": event["id"]})
        ).scalar_one()
        for giver, receiver in zip(participant_ids, participant_ids[1:] + participant_ids[:1], strict=True):
            await other_draw.execute(
                text(
                    "INSERT INTO assignment (draw_id, giver_id, receiver_id, reveal_token) "
                    "VALUES (:draw, :giver, :receiver, :token)"
                ),
                {"draw": draw_id, "giver": giver, "receiver": receiver, "token": f"token-{giver}"},
            )
        await other_draw.execute(text("UPDATE event SET is_draw_complete = true WHERE id = :id"), {"id": event["id"]})
        await other_draw.commit()

    response = await request

    # Checking before locking would have read "not drawn yet" and then collided with the finished draw.
    assert response.status_code == httpx.codes.OK
    assert response.json()["is_draw_complete"] is True
    assert len(await fetch_all("SELECT id FROM draw")) == 1


async def test_a_participant_sees_their_assignment_when_the_draw_lands_while_they_are_being_read(client, monkeypatch):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Cid"])
    access_token = (await fetch_all("SELECT access_token FROM participant ORDER BY id"))[0].access_token
    await close_registration(event["id"])

    read_participant = participant_page.get_participant_by_access_token
    reads = 0

    async def draw_commits_between_the_reads_statements(session, *, access_token):
        nonlocal reads
        participant = await read_participant(session, access_token=access_token)
        reads += 1
        if reads == 1:
            # The read is several statements, each with its own snapshot: the assignments were fetched before the
            # draw committed and the event after it. This leaves the session in exactly that state.
            async with AsyncSessionLocal() as other_request:
                assert await execute_draw_if_due(other_request, event_id=participant.event_id)
            await session.refresh(participant.event)
            assert participant.event.is_draw_complete is True
            assert participant.given_assignments == []
        return participant

    monkeypatch.setattr(participant_page, "get_participant_by_access_token", draw_commits_between_the_reads_statements)

    body = (await client.get(f"/participant/me/{access_token}")).json()

    assert body["event"]["is_draw_complete"] is True
    assert body["assignment"] is not None
