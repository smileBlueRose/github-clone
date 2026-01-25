"""add repositories model

Revision ID: 7122db3a117e
Revises: 4e7010afca13
Create Date: 2026-01-24 06:06:19.375468

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7122db3a117e"
down_revision: Union[str, Sequence[str], None] = "4e7010afca13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "repositories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            name=op.f("fk_repositories_owner_id_users"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_repositories")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("repositories")
