"""Update refresh_tokens

Revision ID: a94dcf0ab5f9
Revises: 09c33cd3f9ca
Create Date: 2026-01-20 10:36:43.860447

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a94dcf0ab5f9"
down_revision: Union[str, Sequence[str], None] = "09c33cd3f9ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "refresh_tokens",
        sa.Column("token_hash", sa.String(length=64), nullable=False),
    )
    op.add_column(
        "refresh_tokens", sa.Column("is_revoked", sa.Boolean(), nullable=False)
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("user_agent", sa.String(length=512), nullable=False),
    )
    op.add_column(
        "refresh_tokens",
        sa.Column("ip_address", sa.String(length=45), nullable=False),
    )
    op.add_column("refresh_tokens", sa.Column("id", sa.UUID(), nullable=False))
    op.drop_index(op.f("ix_refresh_tokens_jti"), table_name="refresh_tokens")
    op.create_index(
        op.f("ix_refresh_tokens_token_hash"),
        "refresh_tokens",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        op.f("ix_refresh_tokens_user_id"),
        "refresh_tokens",
        ["user_id"],
        unique=False,
    )
    op.drop_column("refresh_tokens", "jti")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "refresh_tokens",
        sa.Column("jti", sa.UUID(), autoincrement=False, nullable=False),
    )
    op.drop_index(
        op.f("ix_refresh_tokens_user_id"), table_name="refresh_tokens"
    )
    op.drop_index(
        op.f("ix_refresh_tokens_token_hash"), table_name="refresh_tokens"
    )
    op.create_index(
        op.f("ix_refresh_tokens_jti"), "refresh_tokens", ["jti"], unique=False
    )
    op.drop_column("refresh_tokens", "id")
    op.drop_column("refresh_tokens", "ip_address")
    op.drop_column("refresh_tokens", "user_agent")
    op.drop_column("refresh_tokens", "is_revoked")
    op.drop_column("refresh_tokens", "token_hash")
