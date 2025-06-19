"""update users

Revision ID: a95c47cf13e4
Revises: 6a8bf804a7d5
Create Date: 2025-06-19 18:45:28.349977

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a95c47cf13e4"
down_revision: Union[str, None] = "6a8bf804a7d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users", sa.Column("first_name", sa.String(length=100), nullable=False)
    )
    op.add_column(
        "users", sa.Column("last_name", sa.String(length=100), nullable=False)
    )
    op.add_column("users", sa.Column("username", sa.String(length=20), nullable=False))


def downgrade() -> None:
    op.drop_column("users", "username")
    op.drop_column("users", "last_name")
    op.drop_column("users", "first_name")
