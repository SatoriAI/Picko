import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from source.database.connection import get_session
from source.database.operations import get_assignment_by_token

router = APIRouter(prefix="/draw", tags=["Draw"])


class EventInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    date: datetime.date | None
    max_amount: int | None
    currency: str | None


class AssignmentReveal(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    giver_name: str
    receiver_name: str
    receiver_wishlist: str | None
    event: EventInfo


@router.get(
    "/reveal/{token}",
    status_code=status.HTTP_200_OK,
    response_model=AssignmentReveal,
)
async def reveal_assignment(
    token: str,
    session: AsyncSession = Depends(get_session),
) -> AssignmentReveal:
    if (
        assignment := await get_assignment_by_token(session, reveal_token=token)
    ) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found. The link may be invalid or expired.",
        )

    return AssignmentReveal(
        giver_name=assignment.giver.name,
        receiver_name=assignment.receiver.name,
        receiver_wishlist=assignment.receiver.wishlist,
        event=EventInfo(
            name=assignment.giver.event.name,
            date=assignment.giver.event.date,
            max_amount=assignment.giver.event.max_amount,
            currency=assignment.giver.event.currency,
        ),
    )
