import asyncio
import datetime

import click
from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from source.celery_app import celery_app
from source.database.connection import AsyncSessionLocal
from source.database.models import Assignment, Event, Participant
from source.database.operations import get_event
from source.settings import settings
from source.tasks.draw import draw
from source.utils.datetime import ensure_utc
from source.utils.postman import PostMan

_EMAIL = TypeAdapter(EmailStr)


def _parse_deadline(value: str) -> datetime.datetime:
    raw = value.replace("Z", "+00:00")

    try:
        dt = datetime.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise click.ClickException("Invalid deadline format. Use ISO-8601, e.g. 2025-12-24T19:30:00+00:00") from exc

    return ensure_utc(dt)


async def _get_event_or_fail(session, event_id: int, lock: bool = False) -> Event:
    if (event := await get_event(session, event_id=event_id, lock=lock)) is None:
        raise click.ClickException(f"Event {event_id} not found")
    return event


def _parse_email(value: str) -> str:
    try:
        return _EMAIL.validate_python(value.strip())
    except ValidationError as exc:
        raise click.ClickException(f"Invalid email address: {value}") from exc


async def _get_participant_or_fail(session, event_id: int, name: str) -> Participant:
    result = await session.execute(
        select(Participant).where(Participant.event_id == event_id, Participant.name == name)
    )
    if (participant := result.scalar_one_or_none()) is None:
        raise click.ClickException(f"Participant '{name}' not found in event {event_id}")
    return participant


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


@cli.command("resend-email")
@click.argument("event_id", type=int)
@click.argument("name", type=str)
def resend_email(event_id: int, name: str) -> None:
    async def _run() -> None:
        async with AsyncSessionLocal() as session:
            await _get_event_or_fail(session, event_id)

            result = await session.execute(
                select(Participant)
                .options(
                    selectinload(Participant.event),
                    selectinload(Participant.given_assignments).selectinload(Assignment.receiver),
                )
                .where(Participant.event_id == event_id, Participant.name == name)
            )
            participant = result.scalar_one_or_none()

            if participant is None:
                raise click.ClickException(f"Participant '{name}' not found in event {event_id}")

            if not participant.email:
                raise click.ClickException(f"Participant '{name}' has no email address")

            if not participant.given_assignments:
                raise click.ClickException(f"Participant '{name}' has no assignment (draw not complete?)")

            async with PostMan() as postman:
                sent_to, skipped = await postman.send_event_emails(participants=[participant], event_id=event_id)

            if sent_to:
                click.echo(f"Email sent successfully to {participant.email}.")
            else:
                raise click.ClickException(f"Failed to send email to {participant.email}")

    asyncio.run(_run())


@cli.command("set-email")
@click.argument("event_id", type=int)
@click.argument("name", type=str)
@click.argument("email", type=str)
def set_email(event_id: int, name: str, email: str) -> None:
    new_email = _parse_email(email)

    async def _run() -> None:
        async with AsyncSessionLocal() as session:
            event = await _get_event_or_fail(session, event_id)
            participant = await _get_participant_or_fail(session, event_id, name)
            old_email = participant.email
            participant.email = new_email
            await session.commit()

        click.echo(f"Email of '{name}' in event {event_id} changed: {old_email or '<none>'} -> {new_email}.")
        if event.is_draw_complete:
            click.echo(f'The draw is complete. Send the assignment with: picko resend-email {event_id} "{name}"')

    asyncio.run(_run())


@cli.command("delete-participant")
@click.argument("event_id", type=int)
@click.argument("name", type=str)
def delete_participant(event_id: int, name: str) -> None:
    async def _run() -> None:
        async with AsyncSessionLocal() as session:
            # Lock the event row so a draw cannot start between this check and the delete.
            event = await _get_event_or_fail(session, event_id, lock=True)
            if event.is_draw_complete:
                raise click.ClickException(
                    f"The draw for event {event_id} is complete. Deleting '{name}' would cascade to the assignments "
                    "where they give or receive, leaving their giver without a receiver."
                )

            participant = await _get_participant_or_fail(session, event_id, name)
            await session.delete(participant)
            await session.commit()

        click.echo(f"Participant '{name}' (id={participant.id}) deleted from event {event_id}.")

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
