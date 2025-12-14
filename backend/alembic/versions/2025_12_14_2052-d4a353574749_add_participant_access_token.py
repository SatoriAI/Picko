"""add_participant_access_token

Revision ID: d4a353574749
Revises: aa17f25c1884
Create Date: 2025-12-14 20:52:39.732901

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4a353574749"
down_revision: Union[str, Sequence[str], None] = "aa17f25c1884"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add column as nullable first
    op.add_column(
        "participant", sa.Column("access_token", sa.String(length=64), nullable=True)
    )

    # Backfill existing participants with unique tokens
    op.execute("""
        UPDATE participant
        SET access_token = 'legacy_' || id || '_' || md5(random()::text)
        WHERE access_token IS NULL
    """)

    # Make non-nullable and add unique constraint
    op.alter_column("participant", "access_token", nullable=False)
    op.create_unique_constraint(
        "uq_participant_access_token", "participant", ["access_token"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("uq_participant_access_token", "participant", type_="unique")
    op.drop_column("participant", "access_token")
