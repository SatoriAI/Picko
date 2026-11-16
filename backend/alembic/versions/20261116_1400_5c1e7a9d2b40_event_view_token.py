"""Open the event page by a random token instead of the event id

Revision ID: 5c1e7a9d2b40
Revises: 18e49ddd4710
Create Date: 2026-11-16 14:00:00

Every existing event gets its own token, so their pages move to a new address and the old /event/<id> links stop
working. That is the point: the ids are sequential, and anyone could read every event's names and wishlists by
counting.

Reversible: the downgrade drops the column, and the pages are reachable only by id again.
"""

import secrets
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
    op.add_column("event", sa.Column("view_token", sa.String(length=64), nullable=True))

    # Generated here rather than in SQL: Postgres has no cryptographic random without pgcrypto.
    connection = op.get_bind()
    for (event_id,) in connection.execute(sa.text("SELECT id FROM event")):
        connection.execute(
            sa.text("UPDATE event SET view_token = :token WHERE id = :id"),
            {"token": secrets.token_urlsafe(32), "id": event_id},
        )

    op.alter_column("event", "view_token", nullable=False)
    op.create_unique_constraint("event_view_token_key", "event", ["view_token"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("event_view_token_key", "event", type_="unique")
    op.drop_column("event", "view_token")
