"""Add roles and permissions

Revision ID: b8bf9db4be54
Revises: 0335fe24d3ff
Create Date: 2024-10-13 16:23:07.604460

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8bf9db4be54'
down_revision: Union[str, None] = '0335fe24d3ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Вставка ролей
    op.execute(
        f"""
        INSERT INTO auth.role (id, name) VALUES
        ('{uuid.uuid4()}', 'guest'),
        ('{uuid.uuid4()}', 'subscriber'),
        ('{uuid.uuid4()}', 'administrator');
        """
    )

    # Вставка разрешений
    op.execute(
        f"""
        INSERT INTO auth.permission (id, http_method, resource, name) VALUES
        ('{uuid.uuid4()}', 'GET', 'content', 'view_free_content'),
        ('{uuid.uuid4()}', 'GET', 'content', 'view_premium_content'),
        ('{uuid.uuid4()}', 'PUT', 'roles', 'edit_role'),
        ('{uuid.uuid4()}', 'PUT', 'roles', 'edit_user');
        """
    )

    # Связывание ролей с разрешениями
    op.execute(
        f"""
        INSERT INTO auth.role_permission (role_id, permission_id) VALUES
        ((SELECT id FROM auth.role WHERE name = 'guest'), (SELECT id FROM auth.permission WHERE name = 'view_free_content')),
        ((SELECT id FROM auth.role WHERE name = 'subscriber'), (SELECT id FROM auth.permission WHERE name = 'view_premium_content')),
        ((SELECT id FROM auth.role WHERE name = 'administrator'), (SELECT id FROM auth.permission WHERE name = 'edit_role')),
        ((SELECT id FROM auth.role WHERE name = 'administrator'), (SELECT id FROM auth.permission WHERE name = 'edit_user'));
        """
    )

def downgrade():
    # Удаление связей ролей и разрешений
    op.execute("DELETE FROM auth.role_permission WHERE role_id IN (SELECT id FROM auth.role WHERE name IN ('guest', 'subscriber', 'administrator'))")
    
    # Удаление разрешений
    op.execute("DELETE FROM auth.permission WHERE name IN ('view_free_content', 'view_premium_content', 'edit_role', 'edit_user')")
    
    # Удаление ролей
    op.execute("DELETE FROM auth.role WHERE name IN ('guest', 'subscriber', 'administrator')")
