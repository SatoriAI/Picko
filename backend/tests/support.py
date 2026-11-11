import asyncio
import datetime

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncConnection

from source.database.connection import ENGINE


def in_one_day() -> str:
    return (datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)).isoformat()


async def create_event(client: httpx.AsyncClient, **overrides) -> dict:
    payload = {"name": "Office party", "registration_deadline": in_one_day(), "currency": None} | overrides
    response = await client.post("/event", json=payload)
    assert response.status_code == httpx.codes.CREATED, response.text
    return response.json()


async def register(client: httpx.AsyncClient, token: str, name: str, email: str | None = None) -> httpx.Response:
    return await client.post(f"/event/register/{token}", json={"name": name, "email": email})


async def create_event_with_participants(client: httpx.AsyncClient, names: list[str]) -> dict:
    event = await create_event(client)
    for name in names:
        response = await register(client, event["registration_token"], name, f"{name.lower()}@example.com")
        assert response.status_code == httpx.codes.CREATED, response.text
    return event


async def close_registration(event_id: int) -> None:
    """Move the deadline into the past, which the API itself refuses to do."""
    async with ENGINE.begin() as connection:
        await connection.execute(
            text("UPDATE event SET registration_deadline = now() - interval '1 minute' WHERE id = :id"),
            {"id": event_id},
        )


async def fetch_all(sql: str, **params) -> list:
    async with ENGINE.begin() as connection:
        return list((await connection.execute(text(sql), params)).all())


async def wait_until_a_query_waits_on_a_lock_held_by(holder: AsyncConnection, timeout: float = 15.0) -> None:
    """
    Positive evidence that a query is blocked behind this connection's lock, instead of sleeping and hoping.

    Asking for the holder by pid keeps a lock wait anywhere else in the database from being taken for this one.
    """
    holder_pid = (await holder.execute(text("SELECT pg_backend_pid()"))).scalar_one()
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        blocked = await fetch_all(
            "SELECT count(*) AS total FROM pg_stat_activity WHERE :holder = ANY(pg_blocking_pids(pid))",
            holder=holder_pid,
        )
        if blocked[0].total:
            return
        await asyncio.sleep(0.05)
    raise AssertionError("no query was blocked behind the lock holder")


async def run_the_draw(client: httpx.AsyncClient, event_id: int) -> None:
    await close_registration(event_id)
    response = await client.get(f"/event/{event_id}")
    assert response.json()["is_draw_complete"] is True
