import subprocess
import sys
from pathlib import Path

from tests.support import close_registration, create_event_with_participants, fetch_all, register

BACKEND_DIR = Path(__file__).resolve().parent.parent


def run_cli(*args: str) -> subprocess.CompletedProcess:
    """Each command opens its own event loop, so it runs in its own interpreter, as it does in production."""
    return subprocess.run(
        [sys.executable, "-m", "source.cli", *args],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )


async def test_set_email_gives_a_participant_an_address(client):
    event = await create_event_with_participants(client, ["Ann", "Bob"])
    await register(client, event["registration_token"], "NoEmail")

    result = run_cli("set-email", str(event["id"]), "NoEmail", "found@example.com")

    assert result.returncode == 0, result.stderr[-2000:]
    rows = await fetch_all("SELECT email FROM participant WHERE name = 'NoEmail'")
    assert rows[0].email == "found@example.com"


async def test_set_email_offers_a_resend_once_the_participant_was_emailed(client):
    event = await create_event_with_participants(client, ["Ann", "Bob"])
    await fetch_all("UPDATE participant SET notified_at = now() WHERE name = 'Ann' RETURNING id")

    result = run_cli("set-email", str(event["id"]), "Ann", "ann.new@example.com")

    assert result.returncode == 0, result.stderr[-2000:]
    assert "resend-email" in result.stdout


async def test_delete_participant_removes_an_entry_before_the_draw(client):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Stray"])

    result = run_cli("delete-participant", str(event["id"]), "Stray")

    assert result.returncode == 0, result.stderr[-2000:]
    assert [row.name for row in await fetch_all("SELECT name FROM participant ORDER BY id")] == ["Ann", "Bob"]


async def test_delete_participant_refuses_once_the_draw_is_complete(client):
    event = await create_event_with_participants(client, ["Ann", "Bob", "Cid"])
    await close_registration(event["id"])
    await client.get(f"/event/{event['id']}")

    result = run_cli("delete-participant", str(event["id"]), "Cid")

    assert result.returncode == 1
    assert "is complete" in result.stderr
    assert len(await fetch_all("SELECT id FROM participant")) == 3
    assert len(await fetch_all("SELECT id FROM assignment")) == 3
