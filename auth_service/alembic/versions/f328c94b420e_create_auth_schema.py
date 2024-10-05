"""create auth schema

Revision ID: f328c94b420e
Revises: 
Create Date: 2024-10-04 18:46:56.893968

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.sql.ddl import CreateSchema

# revision identifiers, used by Alembic.
revision: str = 'f328c94b420e'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(text("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_namespace WHERE nspname = 'auth') THEN CREATE SCHEMA auth; END IF; END $$;"))


def downgrade():
    op.execute('DROP SCHEMA IF EXISTS auth CASCADE')
