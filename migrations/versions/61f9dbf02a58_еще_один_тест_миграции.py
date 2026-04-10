"""еще один тест миграции

Revision ID: 61f9dbf02a58
Revises: 685fb8adb198
Create Date: 2026-04-08 22:08:54.856770

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '61f9dbf02a58'
down_revision: Union[str, Sequence[str], None] = '685fb8adb198'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
