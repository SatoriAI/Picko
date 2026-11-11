import secrets
from datetime import UTC, datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from source.database.models import Assignment, Draw, Event, Participant
from source.settings import CurrencySelection, LanguageSelection
from source.utils.distribution import generate_derangement

MIN_PARTICIPANTS_FOR_DRAW = 2


async def get_event(session: AsyncSession, *, event_id: int, lock: bool = False) -> Event | None:
    query = (
        select(Event).options(selectinload(Event.participants), selectinload(Event.draws)).where(Event.id == event_id)
    )
    if lock:
        query = query.with_for_update()
    return (await session.execute(query)).scalar_one_or_none()


async def get_event_by_registration_token(
    session: AsyncSession, *, registration_token: str, lock: bool = False
) -> Event | None:
    query = (
        select(Event)
        .options(selectinload(Event.participants), selectinload(Event.draws))
        .where(Event.registration_token == registration_token)
    )
    if lock:
        # Shared: registrations do not queue behind each other, but all of them queue behind a draw's FOR UPDATE.
        query = query.with_for_update(read=True)
    return (await session.execute(query)).scalar_one_or_none()


async def create_event(
    session: AsyncSession,
    *,
    name: str,
    registration_deadline: datetime,
    max_amount: int | None = None,
    date=None,
    currency: CurrencySelection | None = None,
) -> Event:
    event = Event(
        name=name,
        max_amount=max_amount,
        date=date,
        currency=currency,
        registration_deadline=registration_deadline,
        registration_token=secrets.token_urlsafe(32),
        is_draw_complete=False,
    )

    session.add(event)
    await session.commit()

    # Reload with all relationships to avoid lazy loading issues
    result = await session.execute(
        select(Event).options(selectinload(Event.participants), selectinload(Event.draws)).where(Event.id == event.id)
    )
    return result.scalar_one()


async def register_participant(
    session: AsyncSession,
    *,
    event_id: int,
    name: str,
    email: str | None = None,
    language: LanguageSelection = LanguageSelection.EN,
    wishlist: str | None = None,
) -> Participant:
    participant = Participant(
        event_id=event_id,
        name=name,
        email=email,
        language=language,
        wishlist=wishlist,
        access_token=secrets.token_urlsafe(32),
    )
    session.add(participant)
    await session.commit()
    await session.refresh(participant)
    return participant


def is_draw_due(event: Event, *, participant_count: int) -> bool:
    return (
        not event.is_draw_complete
        and datetime.now(UTC) > event.registration_deadline
        and participant_count >= MIN_PARTICIPANTS_FOR_DRAW
    )


async def execute_draw_if_due(session: AsyncSession, *, event_id: int) -> bool:
    """
    Run the event's draw unless it already ran or is not due yet. Returns whether this call ran it.

    The event row is locked before anything is checked, so concurrent callers queue here and every one after the
    first finds the draw complete. The transaction ends either way, which releases the lock.
    """
    event = (
        await session.execute(
            select(Event).where(Event.id == event_id).with_for_update().execution_options(populate_existing=True)
        )
    ).scalar_one_or_none()
    if event is None:
        await session.commit()
        return False

    result = await session.execute(select(Participant).where(Participant.event_id == event_id).order_by(Participant.id))
    participants = list(result.scalars().all())

    if not is_draw_due(event, participant_count=len(participants)):
        await session.commit()
        return False

    draw = Draw(event_id=event_id)
    session.add(draw)
    await session.flush()

    session.add_all(
        Assignment(
            draw_id=draw.id,
            giver_id=giver.id,
            receiver_id=receiver.id,
            reveal_token=secrets.token_urlsafe(32),
        )
        for giver, receiver in generate_derangement(participants)
    )

    event.is_draw_complete = True
    await session.commit()
    return True


async def get_event_and_maybe_draw(session: AsyncSession, *, event_id: int) -> Event | None:
    event = await get_event(session, event_id=event_id)
    if event is None:
        return None

    # Unlocked look first, so an ordinary read never waits on the event row.
    if is_draw_due(event, participant_count=len(event.participants)):
        await execute_draw_if_due(session, event_id=event_id)
        session.expire_all()
        event = await get_event(session, event_id=event_id)

    return event


async def get_unnotified_participant_ids(session: AsyncSession, *, event_id: int) -> list[int]:
    """Participants who have an assignment and an email address but were not emailed yet."""
    result = await session.execute(
        select(Participant.id)
        .join(Assignment, Assignment.giver_id == Participant.id)
        .where(
            Participant.event_id == event_id,
            Participant.email.is_not(None),
            Participant.notified_at.is_(None),
        )
        .order_by(Participant.id)
    )
    return list(result.scalars().all())


async def claim_unnotified_participant(session: AsyncSession, *, participant_id: int) -> Participant | None:
    """
    Lock a participant for emailing until the transaction ends.

    Returns None when the participant was already emailed or another run holds the claim right now.
    """
    result = await session.execute(
        select(Participant)
        .options(selectinload(Participant.given_assignments))
        .where(Participant.id == participant_id, Participant.notified_at.is_(None))
        .with_for_update(skip_locked=True)
        .execution_options(populate_existing=True)
    )
    return result.scalar_one_or_none()


async def mark_event_notified_if_nobody_is_waiting(session: AsyncSession, *, event_id: int) -> bool:
    """
    Close the event's notifications unless a participant still needs an email. Returns whether it was closed.

    Checked under the event lock, which `set-email` in the CLI also takes: an address added while emails were going
    out is either seen here, or arrives after the event is closed and the CLI says so.
    """
    await session.execute(select(Event.id).where(Event.id == event_id).with_for_update())

    if await get_unnotified_participant_ids(session, event_id=event_id):
        await session.commit()
        return False

    await session.execute(update(Event).where(Event.id == event_id).values(notified_at=datetime.now(UTC)))
    await session.commit()
    return True


async def get_assignment_by_token(session: AsyncSession, *, reveal_token: str) -> Assignment | None:
    result = await session.execute(
        select(Assignment)
        .options(
            selectinload(Assignment.giver).selectinload(Participant.event),
            selectinload(Assignment.receiver),
        )
        .where(Assignment.reveal_token == reveal_token)
    )
    return result.scalar_one_or_none()


async def get_participant_by_access_token(session: AsyncSession, *, access_token: str) -> Participant | None:
    result = await session.execute(
        select(Participant)
        .options(
            selectinload(Participant.event),
            selectinload(Participant.given_assignments).selectinload(Assignment.receiver),
        )
        .where(Participant.access_token == access_token)
    )
    return result.scalar_one_or_none()
