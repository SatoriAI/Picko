import secrets
from random import shuffle

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from source.database.models import Assignment, Draw, Event, Participant


def generate_derangement(
    participants: list[Participant],
) -> list[tuple[Participant, Participant]]:
    n = len(participants)
    if n < 2:
        return []

    indices = list(range(n))
    is_valid = False

    while not is_valid:
        shuffled = indices.copy()
        shuffle(shuffled)
        is_valid = all(i != shuffled[i] for i in range(n))

    return [(participants[i], participants[shuffled[i]]) for i in range(n)]


async def get_event(session: AsyncSession, *, event_id: int) -> Event | None:
    result = await session.execute(
        select(Event)
        .options(
            selectinload(Event.participants).selectinload(
                Participant.given_assignments
            ),
            selectinload(Event.draws),
        )
        .where(Event.id == event_id)
    )
    return result.scalar_one_or_none()


async def get_event_participants_with_assignments(
    session: AsyncSession, *, event_id: int
) -> list[Participant]:
    result = await session.execute(
        select(Participant)
        .options(
            selectinload(Participant.given_assignments).selectinload(
                Assignment.receiver
            ),
            selectinload(Participant.event),
        )
        .where(Participant.event_id == event_id)
    )
    return list(result.scalars().all())


async def create_event(
    session: AsyncSession,
    *,
    name: str,
    participants: list[dict[str, str | None]],
    max_amount: int | None = None,
    date=None,
    currency: str | None = None,
) -> Event:
    event = Event(name=name, max_amount=max_amount, date=date, currency=currency)
    event.participants = [
        Participant(name=p["name"], email=p.get("email")) for p in participants
    ]

    session.add(event)
    await session.flush()  # Get participant IDs

    # Auto-generate the draw
    draw = Draw(event_id=event.id)
    session.add(draw)
    await session.flush()  # Get draw ID

    # Generate derangement and create assignments
    pairs = generate_derangement(event.participants)
    for giver, receiver in pairs:
        assignment = Assignment(
            draw_id=draw.id,
            giver_id=giver.id,
            receiver_id=receiver.id,
            reveal_token=secrets.token_urlsafe(32),
        )
        session.add(assignment)

    await session.commit()

    # Reload with all relationships
    result = await session.execute(
        select(Event)
        .options(
            selectinload(Event.participants).selectinload(
                Participant.given_assignments
            ),
            selectinload(Event.draws).selectinload(Draw.assignments),
        )
        .where(Event.id == event.id)
    )
    return result.scalar_one()


async def update_participant(
    session: AsyncSession,
    *,
    participant_id: int,
    email: str | None,
) -> Participant | None:
    participant = await session.get(Participant, participant_id)
    if participant is None:
        return None

    participant.email = email
    await session.commit()
    await session.refresh(participant)
    return participant


async def get_assignment_by_token(
    session: AsyncSession,
    *,
    reveal_token: str,
) -> Assignment | None:
    result = await session.execute(
        select(Assignment)
        .options(
            selectinload(Assignment.giver).selectinload(Participant.event),
            selectinload(Assignment.receiver),
        )
        .where(Assignment.reveal_token == reveal_token)
    )
    return result.scalar_one_or_none()
