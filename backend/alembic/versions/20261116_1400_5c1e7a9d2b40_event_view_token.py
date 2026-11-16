"""Open the event page by a random token instead of the event id

Revision ID: 5c1e7a9d2b40
Revises: 18e49ddd4710
Create Date: 2026-11-16 14:00:00

Every existing event gets its own token, so their pages move to a new address and the old /event/<id> links stop
working. That is the point: the ids are sequential, and anyone could read every event's names and wishlists by
counting.

The column defaults to gen_random_uuid() in the database. The app sets its own token, but the previous release keeps
serving while this migration runs before the new release starts, and its inserts omit the column. The default covers
those, and also fills the existing rows.

Rolling back takes two steps, in this order: run `alembic downgrade 18e49ddd4710` while this release is still deployed,
then redeploy the previous release. The previous release's pre-deploy `alembic upgrade head` does not know this
revision and fails if the database is still on it.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5c1e7a9d2b40"
down_revision: str | Sequence[str] | None = "18e49ddd4710"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "event",
        sa.Column(
            "view_token", sa.String(length=64), server_default=sa.text("gen_random_uuid()::text"), nullable=False
        ),
    )
    op.create_unique_constraint("event_view_token_key", "event", ["view_token"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("event_view_token_key", "event", type_="unique")
    op.drop_column("event", "view_token")
