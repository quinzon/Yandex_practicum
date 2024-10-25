"""pg_partman_settings

Revision ID: 7955aade077a
Revises: aba31b71e759
Create Date: 2024-10-24 18:31:05.750714

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '7955aade077a'
down_revision: Union[str, None] = 'aba31b71e759'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        """
        SELECT partman.create_parent(p_parent_table => 'auth.login_history',
         p_control => 'timestamp',
         p_interval=> '1 month');
    """
    )

    op.execute(
        """
        UPDATE partman.part_config 
        SET infinite_time_partitions = true,
            retention = '3 months', 
            retention_keep_table=true 
        WHERE parent_table = 'auth.login_history';
        SELECT cron.schedule('@daily', $$CALL partman.run_maintenance_proc()$$);
        """
    )


def downgrade():
    op.execute("""
        DELETE FROM cron.job WHERE command = $$SELECT public.run_maintenance('auth.login_history')$$;
    """)

    op.execute("""
        SELECT public.undo_partition_table('auth.login_history');
    """)
