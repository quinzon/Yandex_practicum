"""Add phone_number and patronymic column on user table

Revision ID: 0efab7dfc651
Revises: 1e6296a1fd82
Create Date: 2025-02-18 16:09:03.366749

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0efab7dfc651'
down_revision: Union[str, None] = '1e6296a1fd82'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user', sa.Column('patronymic', sa.String(50), nullable=True), schema='auth')

    op.add_column('user', sa.Column('phone_number', sa.String(20), nullable=True), schema='auth')


def downgrade():
    op.drop_column('user', 'patronymic', schema='auth')

    op.drop_column('user', 'phone_number', schema='auth')