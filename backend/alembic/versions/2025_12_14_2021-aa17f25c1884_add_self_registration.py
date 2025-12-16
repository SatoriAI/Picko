"""add_self_registration

Revision ID: aa17f25c1884
Revises: 48a429ba019d
Create Date: 2025-12-14 20:21:09.664862

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "aa17f25c1884"
down_revision: str | Sequence[str] | None = "48a429ba019d"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add columns as nullable first, then backfill, then make non-nullable

    # Event columns
    op.add_column(
        "event",
        sa.Column("registration_deadline", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column("event", sa.Column("registration_token", sa.String(length=64), nullable=True))
    op.add_column("event", sa.Column("is_draw_complete", sa.Boolean(), nullable=True))

    # Backfill existing events: set deadline to now, generate unique tokens, mark draws as complete
    op.execute("""
        UPDATE event
        SET registration_deadline = NOW(),
            registration_token = 'legacy_' || id || '_' || md5(random()::text),
            is_draw_complete = TRUE
        WHERE registration_deadline IS NULL
    """)

    # Now make columns non-nullable
    op.alter_column("event", "registration_deadline", nullable=False)
    op.alter_column("event", "registration_token", nullable=False)
    op.alter_column("event", "is_draw_complete", nullable=False)
    op.create_unique_constraint("uq_event_registration_token", "event", ["registration_token"])

    # Participant columns
    op.add_column("participant", sa.Column("language", sa.String(length=5), nullable=True))
    op.add_column("participant", sa.Column("wishlist", sa.String(length=1000), nullable=True))

    # Backfill existing participants with default language
    op.execute("UPDATE participant SET language = 'en' WHERE language IS NULL")
    op.alter_column("participant", "language", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("participant", "wishlist")
    op.drop_column("participant", "language")
    op.drop_constraint("uq_event_registration_token", "event", type_="unique")
    op.drop_column("event", "is_draw_complete")
    op.drop_column("event", "registration_token")
    op.drop_column("event", "registration_deadline")
