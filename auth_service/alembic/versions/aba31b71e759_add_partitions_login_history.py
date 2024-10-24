"""add partitions login history

Revision ID: aba31b71e759
Revises: 04f0c12135c7
Create Date: 2024-10-24 17:00:36.748727

"""
import calendar
import datetime
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'aba31b71e759'
down_revision: Union[str, None] = '04f0c12135c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
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

    now = datetime.datetime.now()
    _, last_day_of_current_month = calendar.monthrange(now.year, now.month)
    year_month_start = now.replace(day=1)
    year_month_end = now.replace(day=last_day_of_current_month)

    create_partition_query = f"""
        CREATE TABLE auth.login_history_{now.strftime('%Y_%m')}_partition
        PARTITION OF auth.login_history
        FOR VALUES FROM ('{year_month_start}') TO ('{year_month_end}');
    """
    op.execute(create_partition_query)

    op.execute("""
        INSERT INTO auth.login_history (id, user_id, timestamp, ip_address, user_agent)
        SELECT id, user_id, timestamp, ip_address, user_agent FROM auth.login_history_parent;
    """)

    op.execute("DROP TABLE auth.login_history_parent;")


def downgrade():
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

    now = datetime.datetime.now()

    op.execute(
        f"ALTER TABLE auth.login_history DETACH PARTITION auth.login_history_{now.strftime('%Y_%m')}_partition")

    op.execute("DROP TABLE IF EXISTS auth.login_history_{now.strftime('%Y_%m')} CASCADE;")

    op.execute("DROP TABLE auth.login_history CASCADE;")

    op.execute("ALTER TABLE auth.login_history_parent RENAME TO login_history;")
