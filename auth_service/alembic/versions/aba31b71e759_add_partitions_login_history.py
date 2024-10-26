"""add partitions login history

Revision ID: aba31b71e759
Revises: 04f0c12135c7
Create Date: 2024-10-24 17:00:36.748727

"""
import os
from alembic import op

# revision identifiers, used by Alembic.
revision = 'aba31b71e759'
down_revision = '04f0c12135c7'


def upgrade():
    if os.getenv('ENV') != 'test':
        op.execute("ALTER TABLE auth.login_history RENAME TO login_history_parent;")

        op.execute("""
            CREATE TABLE auth.login_history (
                id UUID,
                user_id UUID REFERENCES auth.user(id) ON DELETE CASCADE,
                timestamp TIMESTAMPTZ NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                user_agent VARCHAR(255) NOT NULL,
                PRIMARY KEY (id, timestamp)
            ) PARTITION BY RANGE (timestamp);
        """)

        op.execute("""
            CREATE TABLE auth.login_history_template (
                id UUID,
                user_id UUID REFERENCES auth.user(id) ON DELETE CASCADE,
                timestamp TIMESTAMPTZ NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                user_agent VARCHAR(255) NOT NULL,
                PRIMARY KEY (id, timestamp)
            );
        """)
        op.execute("CREATE INDEX idx_login_history_user_id ON auth.login_history_template (user_id);")

        op.execute("""
            SELECT partman.create_parent(
                p_parent_table := 'auth.login_history',
                p_control := 'timestamp',
                p_interval := '1 month',
                p_template_table := 'auth.login_history_template'
            );
        """)

        op.execute("""
            INSERT INTO auth.login_history (id, user_id, timestamp, ip_address, user_agent)
            SELECT id, user_id, timestamp, ip_address, user_agent FROM auth.login_history_parent;
        """)

        op.execute("DROP TABLE auth.login_history_parent;")


def downgrade():
    if os.getenv('ENV') != 'test':
        op.execute("""
            CREATE TABLE auth.login_history_parent (
                id UUID PRIMARY KEY,
                user_id UUID REFERENCES auth.user(id),
                timestamp TIMESTAMPTZ NOT NULL,
                ip_address VARCHAR(45) NOT NULL,
                user_agent VARCHAR(255) NOT NULL
            );
        """)

        op.execute("""
            INSERT INTO auth.login_history_parent (id, user_id, timestamp, ip_address, user_agent)
            SELECT id, user_id, timestamp, ip_address, user_agent FROM auth.login_history;
        """)

        op.execute("DROP TABLE IF EXISTS auth.login_history_template CASCADE;")
        op.execute("DROP TABLE IF EXISTS auth.login_history CASCADE;")
        op.execute("ALTER TABLE auth.login_history_parent RENAME TO login_history;")
