"""empty message

Revision ID: 9dfcb9cfa576
Revises: dd1fb5a9ac05
Create Date: 2025-12-20 13:45:35.748481

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9dfcb9cfa576"
down_revision: str | Sequence[str] | None = "dd1fb5a9ac05"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("event", sa.Column("notified_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("event", "notified_at")
