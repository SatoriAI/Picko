import asyncio
import datetime
from typing import Any

from structlog import get_logger

from source.celery_app import celery_app
from source.database.connection import AsyncSessionLocal
from source.database.operations import execute_draw, get_event, get_event_participants_with_assignments
from source.utils.postman import PostMan

logger = get_logger()


async def _draw_and_notify_async(event_id: int) -> dict[str, Any]:
    async with AsyncSessionLocal() as session:
        if (event := await get_event(session, event_id=event_id)) is None:
            return {"status": "event_not_found", "event_id": event_id}

        now = datetime.datetime.now(datetime.UTC)
        draw_executed = False

        if not event.is_draw_complete and now > event.registration_deadline and len(event.participants) >= 2:
            await execute_draw(session, event)
            draw_executed = True

            session.expire_all()  # Expire all cached objects to force fresh load from database

            if (event := await get_event(session, event_id=event_id)) is None:
                return {"status": "event_not_found_after_draw", "event_id": event_id}

        if not event.is_draw_complete:
            return {"status": "draw_not_complete", "event_id": event_id, "draw_executed": draw_executed}

        participants = await get_event_participants_with_assignments(session, event_id=event_id)

    async with PostMan() as postman:
        sent_to, skipped = await postman.send_event_emails(participants=participants, event_id=event_id)

    logger.info(
        "Draw task finished",
        event_id=event_id,
        draw_executed=draw_executed,
        participants=len(participants),
        sent=len(sent_to),
        skipped=skipped,
    )

    return {
        "status": "emails_sent",
        "event_id": event_id,
        "draw_executed": draw_executed,
        "participants": len(participants),
        "sent_to": sent_to,
        "skipped": skipped,
    }


@celery_app.task(name="draw")
def draw(event_id: int) -> dict[str, Any]:
    return asyncio.run(_draw_and_notify_async(event_id))
