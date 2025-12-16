"""initial

Revision ID: 48a429ba019d
Revises:
Create Date: 2025-12-14 12:40:22.761869

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "48a429ba019d"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("max_amount", sa.Integer(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=True),
        sa.CheckConstraint("max_amount > 0", name="ck_event_max_amount_positive"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "draw",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["event_id"], ["event.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_draw_event_id"), "draw", ["event_id"], unique=False)
    op.create_table(
        "participant",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("event_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(["event_id"], ["event.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id", "name", name="uq_participant_event_id_name"),
    )
    op.create_index(op.f("ix_participant_event_id"), "participant", ["event_id"], unique=False)
    op.create_table(
        "assignment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("draw_id", sa.Integer(), nullable=False),
        sa.Column("giver_id", sa.Integer(), nullable=False),
        sa.Column("receiver_id", sa.Integer(), nullable=False),
        sa.Column("reveal_token", sa.String(length=64), nullable=False),
        sa.CheckConstraint("giver_id <> receiver_id", name="ck_assignment_not_self"),
        sa.ForeignKeyConstraint(["draw_id"], ["draw.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["giver_id"], ["participant.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["receiver_id"], ["participant.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("draw_id", "giver_id"),
        sa.UniqueConstraint("draw_id", "receiver_id"),
        sa.UniqueConstraint("reveal_token"),
    )
    op.create_index(op.f("ix_assignment_draw_id"), "assignment", ["draw_id"], unique=False)
    op.create_index(op.f("ix_assignment_giver_id"), "assignment", ["giver_id"], unique=False)
    op.create_index(op.f("ix_assignment_receiver_id"), "assignment", ["receiver_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_assignment_receiver_id"), table_name="assignment")
    op.drop_index(op.f("ix_assignment_giver_id"), table_name="assignment")
    op.drop_index(op.f("ix_assignment_draw_id"), table_name="assignment")
    op.drop_table("assignment")
    op.drop_index(op.f("ix_participant_event_id"), table_name="participant")
    op.drop_table("participant")
    op.drop_index(op.f("ix_draw_event_id"), table_name="draw")
    op.drop_table("draw")
    op.drop_table("event")
