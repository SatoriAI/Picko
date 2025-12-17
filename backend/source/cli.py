import asyncio
import datetime

import click

from source.celery_app import celery_app
from source.database.connection import AsyncSessionLocal
from source.database.models import Event
from source.database.operations import get_event
from source.settings import settings
from source.tasks.draw import draw
from source.utils.datetime import ensure_utc


def _parse_deadline(value: str) -> datetime.datetime:
    raw = value.replace("Z", "+00:00")

    try:
        dt = datetime.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise click.ClickException("Invalid deadline format. Use ISO-8601, e.g. 2025-12-24T19:30:00+00:00") from exc

    return ensure_utc(dt)


async def _get_event_or_fail(session, event_id: int) -> Event:
    if (event := await get_event(session, event_id=event_id)) is None:
        raise click.ClickException(f"Event {event_id} not found")
    return event


def _schedule_draw_task(event_id: int, deadline: datetime.datetime) -> None:
    countdown = (
        max(0, int((deadline - datetime.datetime.now(datetime.UTC)).total_seconds())) + settings.schedule_buffer_seconds
    )
    result = draw.apply_async(args=[event_id], countdown=countdown)

    click.echo(f"New task has been scheduled. UUID={result.id}")


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli() -> None:
    pass


@cli.command("set-deadline")
@click.argument("event_id", type=int)
@click.argument("deadline", type=str)
@click.option("--revoke-task-id", default=None, help="If provided, revoke this Celery task ID before scheduling.")
@click.option(
    "--terminate", is_flag=True, default=False, help="If revoking, also request termination if the task is running."
)
def set_deadline(event_id: int, deadline: str, revoke_task_id: str | None, terminate: bool) -> None:
    new_deadline = _parse_deadline(deadline)

    async def _run() -> None:
        async with AsyncSessionLocal() as session:
            event = await _get_event_or_fail(session, event_id)
            event.registration_deadline = new_deadline
            await session.commit()

    asyncio.run(_run())

    click.echo(f"Deadline updated successfully to {new_deadline.isoformat()}.")

    if revoke_task_id:
        celery_app.control.revoke(revoke_task_id, terminate=terminate)
        click.echo(f"Task has been revoked (UUID={revoke_task_id}) with termination set to: {terminate}.")

    _schedule_draw_task(event_id, new_deadline)


if __name__ == "__main__":
    cli()
