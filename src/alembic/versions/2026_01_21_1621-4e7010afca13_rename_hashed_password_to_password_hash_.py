"""rename hashed_password to password_hash for users

Revision ID: 4e7010afca13
Revises: 50ba0af2312f
Create Date: 2026-01-21 16:21:59.617161

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4e7010afca13"
down_revision: Union[str, Sequence[str], None] = "50ba0af2312f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("users", "hashed_password", new_column_name="password_hash")


def downgrade() -> None:
    op.alter_column("users", "password_hash", new_column_name="hashed_password")
