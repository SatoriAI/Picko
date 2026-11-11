import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

from sqlalchemy import text

from source.database.connection import ENGINE
from tests.support import (
    close_registration,
    create_event_with_participants,
    fetch_all,
    register,
    wait_until_a_query_waits_on_a_lock,
)

BACKEND_DIR = Path(__file__).resolve().parent.parent


async def start_cli(*args: str) -> asyncio.subprocess.Process:
    """Each command opens its own event loop, so it runs in its own interpreter, as it does in production."""
    return await asyncio.create_subprocess_exec(
        sys.executable,
        "-m",
        "source.cli",
        *args,
        cwd=BACKEND_DIR,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )


async def finish(process: asyncio.subprocess.Process) -> SimpleNamespace:
    stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=60)
    return SimpleNamespace(returncode=process.returncode, stdout=stdout.decode(), stderr=stderr.decode())


async def run_cli(*args: str) -> SimpleNamespace:
    return await finish(await start_cli(*args))


async def email_of(name: str) -> str | None:
    return (await fetch_all("SELECT email FROM participant WHERE name = :name", name=name))[0].email


async def test_set_email_gives_a_participant_an_address(client):
    event = await create_event_with_participants(client, ["Ann", "Bob"])
    await register(client, event["registration_token"], "NoEmail")

    result = await run_cli("set-email", str(event["id"]), "NoEmail", "found@example.com")

    assert result.returncode == 0, result.stderr[-2000:]
    assert await email_of("NoEmail") == "found@example.com"


async def test_set_email_offers_a_resend_once_the_participant_was_emailed(client):
    event = await create_event_with_participants(client, ["Ann", "Bob"])
    await fetch_all("UPDATE participant SET notified_at = now() WHERE name = 'Ann' RETURNING id")

    result = await run_cli("set-email", str(event["id"]), "Ann", "ann.new@example.com")

    assert result.returncode == 0, result.stderr[-2000:]
    assert "Emails already went out" in result.stdout
    assert "resend-email" in result.stdout


async def test_set_email_during_a_send_to_that_participant_offers_a_resend(client):
    event = await create_event_with_participants(client, ["Ann", "Bob"])

    async with ENGINE.connect() as task_sending_to_ann:
        # The task holds the participant's row from claiming them until their email is recorded.
        await task_sending_to_ann.execute(text("SELECT id FROM participant WHERE name = 'Ann' FOR UPDATE"))

        command = await start_cli("set-email", str(event["id"]), "Ann", "ann.new@example.com")
        await wait_until_a_query_waits_on_a_lock()

        await task_sending_to_ann.execute(text("UPDATE participant SET notified_at = now() WHERE name = 'Ann'"))
        await task_sending_to_ann.commit()

    result = await finish(command)

    assert result.returncode == 0, result.stderr[-2000:]
    assert await email_of("Ann") == "ann.new@example.com"
    # The email went to the old address, so the new one needs a resend and the command has to say so.
    assert "Emails already went out" in result.stdout


async def test_set_email_waits_while_the_task_decides_whether_anyone_is_left(client):
    event = await create_event_with_participants(client, ["Ann", "Bob"])
    await register(client, event["registration_token"], "NoEmail")

    async with ENGINE.connect() as task_closing_the_event:
        await task_closing_the_event.execute(
            text("SELECT id FROM event WHERE id = :id FOR UPDATE"), {"id": event["id"]}
        )

        command = await start_cli("set-email", str(event["id"]), "NoEmail", "found@example.com")
        await wait_until_a_query_waits_on_a_lock()
        assert await email_of("NoEmail") is None

        await task_closing_the_event.commit()

    result = await finish(command)

    assert result.returncode == 0, result.stderr[-2000:]
    assert await email_of("NoEmail") == "found@example.com"


async def test_delete_participant_removes_an_entry_before_the_draw(client):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Stray"])

    result = await run_cli("delete-participant", str(event["id"]), "Stray")

    assert result.returncode == 0, result.stderr[-2000:]
    assert [row.name for row in await fetch_all("SELECT name FROM participant ORDER BY id")] == ["Ann", "Bob"]


async def test_delete_participant_refuses_once_the_draw_is_complete(client):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Cid"])
    await close_registration(event["id"])
    await client.get(f"/event/{event['id']}")

    result = await run_cli("delete-participant", str(event["id"]), "Cid")

    assert result.returncode == 1
    assert "is complete" in result.stderr
    assert len(await fetch_all("SELECT id FROM participant")) == 3
    assert len(await fetch_all("SELECT id FROM assignment")) == 3
