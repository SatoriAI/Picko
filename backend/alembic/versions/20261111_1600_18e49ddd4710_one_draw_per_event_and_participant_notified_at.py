"""One draw per event, and per-participant email delivery state

Revision ID: 18e49ddd4710
Revises: 9dfcb9cfa576
Create Date: 2026-11-11 16:00:00

The unique constraint deletes nothing. If an event already holds more than one draw this migration fails and
changes nothing; decide by hand which draw to keep, then run it again:

    SELECT event_id, count(*) FROM draw GROUP BY event_id HAVING count(*) > 1;

Reversible: the downgrade restores the schema. The backfilled notified_at values go with the column, and
event.notified_at, which they were copied from, is untouched.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "18e49ddd4710"
down_revision: str | Sequence[str] | None = "9dfcb9cfa576"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("participant", sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True))
    # Events notified before this column existed must never be emailed again.
    op.execute(
        """
        UPDATE participant
        SET notified_at = event.notified_at
        FROM event
        WHERE event.id = participant.event_id
          AND event.notified_at IS NOT NULL
          AND participant.email IS NOT NULL
        """
    )

    # The unique constraint's own index replaces the plain one.
    op.drop_index(op.f("ix_draw_event_id"), table_name="draw")
    op.create_unique_constraint("uq_draw_event_id", "draw", ["event_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_draw_event_id", "draw", type_="unique")
    op.create_index(op.f("ix_draw_event_id"), "draw", ["event_id"], unique=False)
    op.drop_column("participant", "notified_at")
