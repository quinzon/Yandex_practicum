"""add roles and perms

Revision ID: 04f0c12135c7
Revises: a2369f57d76f
Create Date: 2024-10-21 17:33:59.755921

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04f0c12135c7'
down_revision: Union[str, None] = 'a2369f57d76f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.execute(
        f"""
        INSERT INTO auth.role (id, name) VALUES
        ('{uuid.uuid4()}', 'superadmin');
        """
    )

    permissions = [
        ('GET', 'roles'),
        ('POST', 'roles'),
        ('PUT', 'roles'),
        ('DELETE', 'roles'),
        ('GET', 'permissions'),
        ('POST', 'permissions'),
        ('PUT', 'permissions'),
        ('DELETE', 'permissions'),
    ]

    for method, resource in permissions:
        op.execute(
            f"""
            INSERT INTO auth.permission (id, http_method, resource, name)
            VALUES ('{uuid.uuid4()}', '{method}', '{resource}', '{method.lower()}_{resource}');
            """
        )


    op.execute(
        """
        INSERT INTO auth.role_permission (role_id, permission_id)
        SELECT r.id, p.id
        FROM auth.role r, auth.permission p
        WHERE r.name = 'admin';
        """
    )


def downgrade():
    op.execute(
        """
        DELETE FROM auth.role_permission
        WHERE role_id = (SELECT id FROM auth.role WHERE name = 'admin');
        """
    )

    op.execute(
        """
        DELETE FROM auth.role WHERE name = 'admin';
        """
    )

    op.execute(
        """
        DELETE FROM auth.permission WHERE resource IN ('roles', 'permissions');
        """
    )
