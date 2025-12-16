import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.connection import get_session
from source.database.operations import execute_draw, get_event, get_participant_by_access_token, update_participant

router = APIRouter(prefix="/participant", tags=["Participant"])


class ParticipantUpdate(BaseModel):
    email: EmailStr | None = None


class ParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str | None


class EventInfo(BaseModel):
    id: int
    name: str
    date: datetime.date | None
    max_amount: int | None
    currency: str | None
    registration_deadline: datetime.datetime
    is_draw_complete: bool


class AssignmentInfo(BaseModel):
    receiver_name: str
    receiver_wishlist: str | None


class MyStatusResponse(BaseModel):
    participant_name: str
    event: EventInfo
    assignment: AssignmentInfo | None  # None if draw hasn't happened yet


@router.get("/me/{access_token}", status_code=status.HTTP_200_OK, response_model=MyStatusResponse)
async def get(access_token: str, session: AsyncSession = Depends(get_session)) -> MyStatusResponse:
    if (participant := await get_participant_by_access_token(session, access_token=access_token)) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found. The link may be invalid."
        )

    if (event := await get_event(session, event_id=participant.event_id)) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found for participant.")

    # Auto-trigger draw if deadline has passed and draw not yet complete
    now = datetime.datetime.now(datetime.UTC)
    if not event.is_draw_complete and now > event.registration_deadline and len(event.participants) >= 2:
        await execute_draw(session, event)

        # Reload participant to get the new assignment
        if (participant := await get_participant_by_access_token(session, access_token=access_token)) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found after draw.")
        event = participant.event

    # Build assignment info if draw is complete
    assignment = None
    if event.is_draw_complete and participant.given_assignments:
        assignment_obj = participant.given_assignments[0]
        assignment = AssignmentInfo(
            receiver_name=assignment_obj.receiver.name,
            receiver_wishlist=assignment_obj.receiver.wishlist,
        )

    return MyStatusResponse(
        participant_name=participant.name,
        event=EventInfo(
            id=event.id,
            name=event.name,
            date=event.date,
            max_amount=event.max_amount,
            currency=event.currency,
            registration_deadline=event.registration_deadline,
            is_draw_complete=event.is_draw_complete,
        ),
        assignment=assignment,
    )


@router.patch("/{participant_id}", status_code=status.HTTP_200_OK, response_model=ParticipantRead)
async def patch(
    participant_id: int, payload: ParticipantUpdate, session: AsyncSession = Depends(get_session)
) -> ParticipantRead:
    try:
        participant = await update_participant(
            session,
            participant_id=participant_id,
            email=str(payload.email).strip() if payload.email else None,
        )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Participant could not be updated due to a database constraint.",
        ) from exc

    if participant is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found")

    return participant
