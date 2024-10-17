"""Add superuser with administrator role

Revision ID: b83e13979655
Revises: b8bf9db4be54
Create Date: 2024-10-17 20:35:52.125719

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
from sqlalchemy.exc import IntegrityError


# revision identifiers, used by Alembic.
revision: str = 'b83e13979655'
down_revision: Union[str, None] = 'b8bf9db4be54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Создание пользователя
    user_id = uuid.uuid4()
    email = "su@world.com"
    password_hash = "$2b$12$IHL.GfWzADXjVab63WJKI.aUtFTuofobzqiJMIB.yWwAuwShK0Asq" 

    try:
        # Вставка нового пользователя
        op.execute(
            f"""INSERT INTO auth.user (id, email, password_hash, created_at, updated_at) 
            VALUES ('{user_id}', '{email}', '{password_hash}', NOW(), NOW())
            """
        )
        
    except IntegrityError:
        print("User already exists.")
        
    try: 
        # Назначение роли пользователю
        op.execute(
            f"INSERT INTO auth.user_role (user_id, role_id) VALUES ( (SELECT id FROM auth.user WHERE id = '{user_id}'), (SELECT id FROM auth.role WHERE name = 'administrator') )"
        )
    except IntegrityError:
        print("Role not found.")

def downgrade():
    op.execute(f"DELETE FROM auth.user_role WHERE user_id = (SELECT id FROM auth.user WHERE email = '{email}')")
    op.execute(f"DELETE FROM auth.user WHERE email = '{email}'")
