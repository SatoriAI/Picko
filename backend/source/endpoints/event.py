import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.connection import get_session
from source.database.operations import (
    create_event,
    get_event,
    get_event_participants_with_assignments,
)

from structlog import get_logger

logger = get_logger()

router = APIRouter(prefix="/event", tags=["Event"])


class ParticipantCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: str | None = Field(default=None, max_length=255)


class EventCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    max_amount: int | None = Field(default=None, gt=0)
    date: datetime.date | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    participants: list[ParticipantCreate] = Field(min_length=1)

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not (value := value.strip()):
            return None
        return value.upper()


class ParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str | None
    reveal_token: str | None = None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    max_amount: int | None
    date: datetime.date | None
    currency: str | None
    participants: list[ParticipantRead]


def build_event_response(event) -> EventRead:
    participants = []
    for p in event.participants:
        reveal_token = None
        if p.given_assignments:
            reveal_token = p.given_assignments[0].reveal_token
        participants.append(
            ParticipantRead(
                id=p.id,
                name=p.name,
                email=p.email,
                reveal_token=reveal_token,
            )
        )
    return EventRead(
        id=event.id,
        name=event.name,
        max_amount=event.max_amount,
        date=event.date,
        currency=event.currency,
        participants=participants,
    )


@router.get("/{event_id}", status_code=status.HTTP_200_OK, response_model=EventRead)
async def get(event_id: int, session: AsyncSession = Depends(get_session)) -> EventRead:
    event = await get_event(session, event_id=event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return build_event_response(event)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EventRead)
async def create(
    payload: EventCreate, session: AsyncSession = Depends(get_session)
) -> EventRead:
    try:
        event = await create_event(
            session,
            name=payload.name,
            max_amount=payload.max_amount,
            date=payload.date,
            currency=payload.currency,
            participants=[
                {"name": p.name.strip(), "email": p.email.strip() if p.email else None}
                for p in payload.participants
            ],
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event could not be created due to a database constraint.",
        ) from exc

    return build_event_response(event)


class SendEmailsResponse(BaseModel):
    sent_count: int
    skipped_count: int
    sent_to: list[str]


@router.post(
    "/{event_id}/send-emails",
    status_code=status.HTTP_200_OK,
    response_model=SendEmailsResponse,
)
async def send_emails(
    event_id: int,
    session: AsyncSession = Depends(get_session),
) -> SendEmailsResponse:
    participants = await get_event_participants_with_assignments(
        session, event_id=event_id
    )

    if not participants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or has no participants",
        )

    sent_to: list[str] = []
    skipped_count = 0

    for participant in participants:
        if not participant.email:
            skipped_count += 1
            continue

        if not participant.given_assignments:
            skipped_count += 1
            continue

        assignment = participant.given_assignments[0]
        receiver_name = assignment.receiver.name
        event = participant.event

        # TODO: Replace with actual email sending when SMTP is configured
        logger.info(
            "Would send email",
            to=participant.email,
            participant_name=participant.name,
            receiver_name=receiver_name,
            event_name=event.name,
            reveal_token=assignment.reveal_token,
        )

        sent_to.append(participant.name)

    return SendEmailsResponse(
        sent_count=len(sent_to),
        skipped_count=skipped_count,
        sent_to=sent_to,
    )
