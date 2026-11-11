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
    mark_event_notified,
)
from source.settings import settings
from source.utils.postman import PostMan, PostManSendError

logger = get_logger()

MAX_RETRIES = 5
RETRY_BASE_SECONDS = 60


async def _email_unnotified_participants(session: AsyncSession, *, event_id: int) -> tuple[int, int]:
    """
    Email every participant who was not emailed yet. Returns (sent, failed).

    Each participant is claimed, emailed and marked in a transaction of their own, so a failure or a crash keeps
    what was already delivered, and a second run of this task for the same event skips whoever the first holds.
    """
    sent = failed = 0

    async with PostMan() as postman:
        for participant_id in await get_unnotified_participant_ids(session, event_id=event_id):
            participant = await claim_unnotified_participant(session, participant_id=participant_id)
            if participant is None:
                continue

            try:
                await postman.send_assignment_email(participant, event_id=event_id)
            except PostManSendError as exc:
                logger.exception(
                    "Failed to send email", participant_id=participant_id, event_id=event_id, error=str(exc)
                )
                await session.rollback()
                failed += 1
                continue

            participant.notified_at = datetime.now(UTC)
            await session.commit()
            sent += 1

            # Smooth bursts to reduce chance of hitting provider rate limits.
            if settings.resend_min_interval_seconds > 0:
                await asyncio.sleep(settings.resend_min_interval_seconds)

    return sent, failed


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

        sent, failed = await _email_unnotified_participants(session, event_id=event_id)

        if failed == 0:
            await mark_event_notified(session, event_id=event_id)

    return {
        "status": "emails_sent" if failed == 0 else "emails_failed",
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
    result = asyncio.run(_run(event_id))

    if result.get("failed"):
        # Only the participants still missing an email are tried again.
        raise self.retry(countdown=RETRY_BASE_SECONDS * 2**self.request.retries)

    return result
