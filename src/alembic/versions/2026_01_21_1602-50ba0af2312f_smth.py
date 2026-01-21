"""smth

Revision ID: 50ba0af2312f
Revises: 18e389cf261d
Create Date: 2026-01-21 16:02:38.576949

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "50ba0af2312f"
down_revision: Union[str, Sequence[str], None] = "18e389cf261d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "refresh_tokens",
        "user_agent",
        existing_type=sa.VARCHAR(length=512),
        nullable=True,
    )
    op.alter_column(
        "refresh_tokens",
        "ip_address",
        existing_type=sa.VARCHAR(length=45),
        nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "refresh_tokens",
        "ip_address",
        existing_type=sa.VARCHAR(length=45),
        nullable=False,
    )
    op.alter_column(
        "refresh_tokens",
        "user_agent",
        existing_type=sa.VARCHAR(length=512),
        nullable=False,
    )
