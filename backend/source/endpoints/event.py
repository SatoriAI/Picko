import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.connection import get_session
from source.database.operations import (
    create_event,
    get_event_and_maybe_draw,
    get_event_by_registration_token,
    get_event_participants_with_assignments,
    register_participant,
)
from source.settings import settings
from source.utils.postman import PostMan, PostManConfigError

from structlog import get_logger

logger = get_logger()

router = APIRouter(prefix="/event", tags=["Event"])


# ============================================================================
# Request/Response Models
# ============================================================================


class EventCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    max_amount: int | None = Field(default=None, gt=0)
    date: datetime.date | None = None
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    registration_deadline: datetime.datetime

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
    language: str
    wishlist: str | None
    reveal_token: str | None = None


class EventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    max_amount: int | None
    date: datetime.date | None
    currency: str | None
    registration_deadline: datetime.datetime
    registration_token: str
    is_draw_complete: bool
    participants: list[ParticipantRead]


class ParticipantRegister(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr | None = None
    language: str = Field(default="en", pattern=r"^(en|pl)$")
    wishlist: str | None = Field(default=None, max_length=1000)


class ParticipantRegistered(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str | None
    language: str
    wishlist: str | None
    event_id: int
    access_token: str


class SendEmailsResponse(BaseModel):
    sent_count: int
    skipped_count: int
    sent_to: list[str]


# ============================================================================
# Helper Functions
# ============================================================================


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
                language=p.language,
                wishlist=p.wishlist,
                reveal_token=reveal_token,
            )
        )
    return EventRead(
        id=event.id,
        name=event.name,
        max_amount=event.max_amount,
        date=event.date,
        currency=event.currency,
        registration_deadline=event.registration_deadline,
        registration_token=event.registration_token,
        is_draw_complete=event.is_draw_complete,
        participants=participants,
    )


# ============================================================================
# Event Endpoints
# ============================================================================


@router.get("/{event_id}", status_code=status.HTTP_200_OK, response_model=EventRead)
async def get(event_id: int, session: AsyncSession = Depends(get_session)) -> EventRead:
    """Get event by ID. Automatically triggers draw if deadline has passed."""
    event = await get_event_and_maybe_draw(session, event_id=event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return build_event_response(event)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=EventRead)
async def create(
    payload: EventCreate, session: AsyncSession = Depends(get_session)
) -> EventRead:
    """Create a new event. Participants self-register via the registration token."""
    try:
        event = await create_event(
            session,
            name=payload.name,
            max_amount=payload.max_amount,
            date=payload.date,
            currency=payload.currency,
            registration_deadline=payload.registration_deadline,
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Event could not be created due to a database constraint.",
        ) from exc

    return build_event_response(event)


# ============================================================================
# Registration Endpoints
# ============================================================================


@router.get(
    "/register/{token}", status_code=status.HTTP_200_OK, response_model=EventRead
)
async def get_event_for_registration(
    token: str, session: AsyncSession = Depends(get_session)
) -> EventRead:
    """Get event info by registration token (for the registration page)."""
    event = await get_event_by_registration_token(session, registration_token=token)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )
    return build_event_response(event)


@router.post(
    "/register/{token}",
    status_code=status.HTTP_201_CREATED,
    response_model=ParticipantRegistered,
)
async def register_for_event(
    token: str,
    payload: ParticipantRegister,
    session: AsyncSession = Depends(get_session),
) -> ParticipantRegistered:
    """Register as a participant for an event."""
    event = await get_event_by_registration_token(session, registration_token=token)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    # Check if registration deadline has passed
    now = datetime.datetime.now(datetime.timezone.utc)
    if now > event.registration_deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration deadline has passed",
        )

    try:
        participant = await register_participant(
            session,
            event_id=event.id,
            name=payload.name.strip(),
            email=str(payload.email).strip() if payload.email else None,
            language=payload.language,
            wishlist=payload.wishlist.strip() if payload.wishlist else None,
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A participant with this name already exists for this event.",
        ) from exc

    return ParticipantRegistered(
        id=participant.id,
        name=participant.name,
        email=participant.email,
        language=participant.language,
        wishlist=participant.wishlist,
        event_id=participant.event_id,
        access_token=participant.access_token,
    )


# ============================================================================
# Email Endpoints
# ============================================================================


@router.post(
    "/{event_id}/send-emails",
    status_code=status.HTTP_200_OK,
    response_model=SendEmailsResponse,
)
async def send_emails(
    event_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> SendEmailsResponse:
    """Send Secret Santa assignment emails to all participants with email addresses."""
    participants = await get_event_participants_with_assignments(
        session, event_id=event_id
    )

    if not participants:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found or has no participants",
        )

    try:
        postman = PostMan(settings)
    except PostManConfigError as exc:
        logger.exception("Email sending is not configured", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email sending is not configured on the server.",
        ) from exc

    sent_to, skipped_count = await postman.send_event_emails(
        participants=participants,
        event_id=event_id,
        request=request,
        cors_origins=settings.cors_origins,
        app_name="Picko",
    )

    return SendEmailsResponse(
        sent_count=len(sent_to),
        skipped_count=skipped_count,
        sent_to=sent_to,
    )
