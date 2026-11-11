import asyncio
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from structlog import get_logger

from source.celery_app import celery_app
from source.database.connection import ENGINE, AsyncSessionLocal
from source.database.operations import (
    claim_unnotified_participant,
    execute_draw_if_due,
    get_event,
    get_unnotified_participant_ids,
    mark_event_notified_if_nobody_is_waiting,
)
from source.settings import settings
from source.utils.postman import PostMan

logger = get_logger()

MAX_RETRIES = 5
RETRY_BASE_SECONDS = 60

# Outcomes that leave someone unemailed. "Elsewhere" is usually another run of this task, which finishes the job, but
# it can also be `set-email` holding the row for a moment, and then nobody else would come back for that participant.
UNFINISHED = frozenset({"emails_failed", "emails_in_progress_elsewhere"})


async def _email_unnotified_participants(session: AsyncSession, *, event_id: int) -> tuple[int, int, int]:
    """
    Email every participant who was not emailed yet. Returns (sent, failed, claimed_elsewhere).

    Each participant is claimed, emailed and marked in a transaction of their own, so a failure or a crash keeps
    what was already delivered, and a second run of this task for the same event skips whoever the first holds.
    """
    sent = failed = claimed_elsewhere = 0

    async with PostMan() as postman:
        for participant_id in await get_unnotified_participant_ids(session, event_id=event_id):
            participant = await claim_unnotified_participant(session, participant_id=participant_id)
            if participant is None:
                claimed_elsewhere += 1
                continue

            try:
                await postman.send_assignment_email(participant, event_id=event_id)
                participant.notified_at = datetime.now(UTC)
                await session.commit()
            except Exception as exc:
                # Anything, not only a refused send: one participant's failure must not cost the others their email.
                logger.exception(
                    "Failed to send email", participant_id=participant_id, event_id=event_id, error=str(exc)
                )
                await session.rollback()
                failed += 1
                continue

            sent += 1

            # Smooth bursts to reduce chance of hitting provider rate limits.
            if settings.resend_min_interval_seconds > 0:
                await asyncio.sleep(settings.resend_min_interval_seconds)

    return sent, failed, claimed_elsewhere


async def draw_and_notify(event_id: int) -> dict[str, Any]:
    async with AsyncSessionLocal() as session:
        if (event := await get_event(session, event_id=event_id)) is None:
            return {"status": "event_not_found", "event_id": event_id}

        if event.notified_at is not None:
            return {"status": "already_notified", "event_id": event_id}

        # Refreshes `event` in place: it is the same row, re-read under the lock.
        draw_executed = await execute_draw_if_due(session, event_id=event_id)

        if not event.is_draw_complete:
            return {"status": "draw_not_complete", "event_id": event_id, "draw_executed": draw_executed}

        sent = 0
        notified = False
        while True:
            sent_now, failed, claimed_elsewhere = await _email_unnotified_participants(session, event_id=event_id)
            sent += sent_now
            if failed:
                break
            if notified := await mark_event_notified_if_nobody_is_waiting(session, event_id=event_id):
                break
            if claimed_elsewhere and sent_now == 0:
                # Whoever is left is locked by someone else right now. The task comes back for them on a retry.
                break
            # Otherwise someone gained an address after this pass listed who to email: go round again.

    if notified:
        status = "emails_sent"
    elif failed:
        status = "emails_failed"
    else:
        status = "emails_in_progress_elsewhere"

    return {
        "status": status,
        "event_id": event_id,
        "draw_executed": draw_executed,
        "sent": sent,
        "failed": failed,
    }


async def _run(event_id: int) -> dict[str, Any]:
    try:
        return await draw_and_notify(event_id)
    finally:
        # Every task runs in a fresh event loop; a pooled connection must not outlive the loop that opened it.
        await ENGINE.dispose()


@celery_app.task(name="draw", bind=True, max_retries=MAX_RETRIES)
def draw(self, event_id: int) -> dict[str, Any]:
    countdown = RETRY_BASE_SECONDS * 2**self.request.retries

    try:
        result = asyncio.run(_run(event_id))
    except Exception as exc:
        # A lost database or anything unforeseen. What was delivered is already recorded, so a rerun is safe.
        raise self.retry(exc=exc, countdown=countdown) from exc

    if result["status"] in UNFINISHED:
        # Only the participants still missing an email are tried again; a retry that finds the event closed is a no-op.
        raise self.retry(countdown=countdown)

    return result
