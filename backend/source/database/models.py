from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Event(Base):
    __tablename__ = "event"
    __table_args__ = (
        CheckConstraint("max_amount > 0", name="ck_event_max_amount_positive"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date: Mapped[date | None] = mapped_column(Date(), nullable=True)

    # Expenses
    max_amount: Mapped[int | None] = mapped_column(Integer(), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)

    # Registration
    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    registration_token: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True
    )
    is_draw_complete: Mapped[bool] = mapped_column(
        Boolean(), default=False, nullable=False
    )

    # SQL Alchemy Relations
    participants: Mapped[list["Participant"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
    draws: Mapped[list["Draw"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )


class Participant(Base):
    __tablename__ = "participant"
    __table_args__ = (
        UniqueConstraint("event_id", "name", name="uq_participant_event_id_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Relations
    event_id: Mapped[int] = mapped_column(
        ForeignKey("event.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="en", nullable=False)
    wishlist: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Personal access token - allows participant to view their own assignment
    access_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    # SQL Alchemy Relations
    event: Mapped["Event"] = relationship(back_populates="participants")
    given_assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="giver",
        foreign_keys="Assignment.giver_id",
        passive_deletes=True,
    )
    received_assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="receiver",
        foreign_keys="Assignment.receiver_id",
        passive_deletes=True,
    )


class Draw(Base):
    __tablename__ = "draw"

    id: Mapped[int] = mapped_column(primary_key=True)

    event_id: Mapped[int] = mapped_column(
        ForeignKey("event.id", ondelete="CASCADE"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),  # pylint: disable=not-callable
    )

    # SQL Alchemy Relations
    event: Mapped["Event"] = relationship(back_populates="draws")
    assignments: Mapped[list["Assignment"]] = relationship(
        back_populates="draw", cascade="all, delete-orphan"
    )


class Assignment(Base):
    __tablename__ = "assignment"
    __table_args__ = (
        CheckConstraint("giver_id <> receiver_id", name="ck_assignment_not_self"),
        UniqueConstraint("draw_id", "giver_id"),
        UniqueConstraint("draw_id", "receiver_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    draw_id: Mapped[int] = mapped_column(
        ForeignKey("draw.id", ondelete="CASCADE"), nullable=False, index=True
    )
    giver_id: Mapped[int] = mapped_column(
        ForeignKey("participant.id", ondelete="CASCADE"), nullable=False, index=True
    )
    receiver_id: Mapped[int] = mapped_column(
        ForeignKey("participant.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # One "secret link" per giver to reveal their receiver.
    reveal_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    # SQL Alchemy Relations
    draw: Mapped["Draw"] = relationship(back_populates="assignments")
    giver: Mapped["Participant"] = relationship(
        back_populates="given_assignments",
        foreign_keys=[giver_id],
    )
    receiver: Mapped["Participant"] = relationship(
        back_populates="received_assignments",
        foreign_keys=[receiver_id],
    )
