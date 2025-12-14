from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.connection import get_session
from source.database.operations import update_participant

router = APIRouter(prefix="/participant", tags=["Participant"])


class ParticipantUpdate(BaseModel):
    email: EmailStr | None = None


class ParticipantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str | None


@router.patch(
    "/{participant_id}", status_code=status.HTTP_200_OK, response_model=ParticipantRead
)
async def patch_participant(
    participant_id: int,
    payload: ParticipantUpdate,
    session: AsyncSession = Depends(get_session),
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Participant not found"
        )

    return participant
