"""edit user for oauth2

Revision ID: d275681961f3
Revises: 04f0c12135c7
Create Date: 2024-10-23 17:31:12.115590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd275681961f3'
down_revision: Union[str, None] = '04f0c12135c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user', sa.Column('provider', sa.String(length=255), nullable=True), schema='auth')
    op.add_column('user', sa.Column('provider_user_id', sa.String(length=255), nullable=True), schema='auth')

    op.create_index('idx_user_provider', 'user', ['provider', 'provider_user_id'], unique=True, schema='auth')


def downgrade():
    op.drop_index('idx_user_provider', table_name='user', schema='auth')
    op.drop_column('user', 'provider', schema='auth')
    op.drop_column('user', 'provider_user_id', schema='auth')
