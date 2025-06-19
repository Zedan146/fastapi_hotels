"""update user

Revision ID: b39061f10dd5
Revises: a95c47cf13e4
Create Date: 2025-06-19 20:57:39.695894

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b39061f10dd5"
down_revision: Union[str, None] = "a95c47cf13e4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")
