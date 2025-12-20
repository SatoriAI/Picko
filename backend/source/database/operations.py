import secrets
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from source.database.models import Assignment, Draw, Event, Participant
from source.settings import CurrencySelection, LanguageSelection
from source.utils.distribution import generate_derangement


async def get_event(session: AsyncSession, *, event_id: int, lock: bool = False) -> Event | None:
    query = select(Event)
    if lock:
        query = query.with_for_update()
    query = query.options(
        selectinload(Event.participants).selectinload(Participant.given_assignments),
        selectinload(Event.draws),
    )
    query = query.where(Event.id == event_id)
    return (await session.execute(query)).scalar_one_or_none()


async def get_event_by_registration_token(session: AsyncSession, *, registration_token: str) -> Event | None:
    result = await session.execute(
        select(Event)
        .options(
            selectinload(Event.participants).selectinload(Participant.given_assignments),
            selectinload(Event.draws),
        )
        .where(Event.registration_token == registration_token)
    )
    return result.scalar_one_or_none()


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
        select(Event)
        .options(
            selectinload(Event.participants).selectinload(Participant.given_assignments),
            selectinload(Event.draws),
        )
        .where(Event.id == event.id)
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


async def execute_draw(session: AsyncSession, event: Event) -> None:
    if event.is_draw_complete:
        return  # Already done

    result = await session.execute(select(Participant).where(Participant.event_id == event.id).order_by(Participant.id))
    participants = list(result.scalars().all())

    if len(participants) < 2:
        return  # Not enough participants

    # Create the draw
    draw = Draw(event_id=event.id)
    session.add(draw)
    await session.flush()

    # Generate derangement and create assignments
    pairs = generate_derangement(participants)
    for giver, receiver in pairs:
        assignment = Assignment(
            draw_id=draw.id,
            giver_id=giver.id,
            receiver_id=receiver.id,
            reveal_token=secrets.token_urlsafe(32),
        )
        session.add(assignment)

    # Mark event as draw complete
    event.is_draw_complete = True
    await session.commit()


async def get_event_and_maybe_draw(session: AsyncSession, *, event_id: int) -> Event | None:
    event = await get_event(session, event_id=event_id)
    if event is None:
        return None

    now = datetime.now(UTC)
    if not event.is_draw_complete and now > event.registration_deadline and len(event.participants) >= 2:
        await execute_draw(session, event)
        # Reload to get the new assignments
        event = await get_event(session, event_id=event_id)

    return event


async def get_event_participants_with_assignments(session: AsyncSession, *, event_id: int) -> list[Participant]:
    result = await session.execute(
        select(Participant)
        .options(
            selectinload(Participant.given_assignments).selectinload(Assignment.receiver),
            selectinload(Participant.event),
        )
        .where(Participant.event_id == event_id)
    )
    return list(result.scalars().all())


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
