"""Merge heads

Revision ID: 37b1d87a4345
Revises: a2369f57d76f, b83e13979655
Create Date: 2024-10-18 19:47:02.145172

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37b1d87a4345'
down_revision: Union[str, None] = ('a2369f57d76f', 'b83e13979655')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
