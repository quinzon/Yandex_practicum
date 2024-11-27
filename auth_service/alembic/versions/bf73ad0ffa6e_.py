"""empty message

Revision ID: bf73ad0ffa6e
Revises: 7955aade077a, d275681961f3
Create Date: 2024-11-26 14:13:50.204696

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf73ad0ffa6e'
down_revision: Union[str, None] = ('7955aade077a', 'd275681961f3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
