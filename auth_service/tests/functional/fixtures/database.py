import uuid
from datetime import datetime

import pytest_asyncio
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.extras import RealDictCursor
from auth_service.tests.functional.settings import test_settings
import bcrypt


@pytest_asyncio.fixture(scope='function', autouse=True)
async def clear_db():
    """
    Clean database before each test.
    """
    conn = psycopg2.connect(
        dbname=test_settings.postgres_db,
        user=test_settings.postgres_user,
        password=test_settings.postgres_password,
        host=test_settings.postgres_host,
        port=test_settings.postgres_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    # getting all tables
    cur.execute("""
        SELECT tablename FROM pg_tables
        WHERE schemaname = 'auth';
    """)
    tables = cur.fetchall()

    for table in tables:
        cur.execute(f'TRUNCATE TABLE "auth"."{table[0]}" RESTART IDENTITY CASCADE')

    cur.close()
    conn.close()


@pytest_asyncio.fixture(scope='function')
async def setup_roles(request):
    roles = request.param

    conn = psycopg2.connect(
        dbname=test_settings.postgres_db,
        user=test_settings.postgres_user,
        password=test_settings.postgres_password,
        host=test_settings.postgres_host,
        port=test_settings.postgres_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    role_names = []
    for role in roles:
        role_name = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO auth.role (id, name) VALUES (%s, %s);
        """, (role_name, role['name']))
        role_names.append(role_name)

    conn.commit()

    yield role_names

    for role_name in role_names:
        cur.execute("""
            DELETE FROM auth.user_role WHERE role_id = %s;
        """, (role_name,))

        cur.execute("""
            DELETE FROM auth.role WHERE id = %s;
        """, (role_name,))

    conn.commit()

    cur.close()
    conn.close()


@pytest_asyncio.fixture(scope='function')
async def setup_permissions(request):
    permissions = request.param

    conn = psycopg2.connect(
        dbname=test_settings.postgres_db,
        user=test_settings.postgres_user,
        password=test_settings.postgres_password,
        host=test_settings.postgres_host,
        port=test_settings.postgres_port
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()

    permission_ids = []

    for permission in permissions:
        permission_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO auth.permission (id, name, http_method, resource) VALUES (%s, %s, %s, %s);
        """, (permission_id, permission['name'], permission['http_method'], permission['resource']))
        permission_ids.append(permission_id)

    conn.commit()

    yield permission_ids

    for permission_id in permission_ids:
        cur.execute("""
            DELETE FROM auth.role_permission WHERE permission_id = %s;
        """, (permission_id,))

        cur.execute("""
            DELETE FROM auth.permission WHERE id = %s;
        """, (permission_id,))

    conn.commit()

    cur.close()
    conn.close()


@pytest_asyncio.fixture(scope='function')
async def setup_user(request):
    user_data = request.param

    conn = psycopg2.connect(
        dbname=test_settings.postgres_db,
        user=test_settings.postgres_user,
        password=test_settings.postgres_password,
        host=test_settings.postgres_host,
        port=test_settings.postgres_port
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    user_id = str(uuid.uuid4())
    now = datetime.now()

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), salt).decode('utf-8')

    cur.execute("""
        INSERT INTO auth.user (id, email, password_hash, first_name, last_name, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (
        user_id,
        user_data['email'],
        password_hash,
        user_data.get('first_name'),
        user_data.get('last_name'),
        now,
        now
    ))
    conn.commit()

    yield user_id

    if user_id:
        cur.execute("""
            DELETE FROM auth.login_history WHERE user_id = %s;
        """, (user_id,))
        cur.execute("""
            DELETE FROM auth.refresh_token WHERE user_id = %s;
        """, (user_id,))
        cur.execute("""
            DELETE FROM auth.user_role WHERE user_id = %s;
        """, (user_id,))
        cur.execute("""
            DELETE FROM auth.user WHERE id = %s;
        """, (user_id,))

    conn.commit()
    cur.close()
    conn.close()


@pytest_asyncio.fixture(scope='function')
async def setup_superuser(request):
    superuser_data = request.param

    conn = psycopg2.connect(
        dbname=test_settings.postgres_db,
        user=test_settings.postgres_user,
        password=test_settings.postgres_password,
        host=test_settings.postgres_host,
        port=test_settings.postgres_port
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor(cursor_factory=RealDictCursor)

    superuser_role_name = 'superadmin'

    cur.execute("""
        SELECT id FROM auth.role WHERE name = %s;
    """, (superuser_role_name,))

    superuser_role = cur.fetchone()

    if not superuser_role:
        role_name = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO auth.role (id, name) VALUES (%s, %s);
        """, (role_name, superuser_role_name))
        conn.commit()
        superuser_role_id = role_name
    else:
        superuser_role_id = superuser_role['id']

    superuser_id = str(uuid.uuid4())
    now = datetime.now()

    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(superuser_data['password'].encode('utf-8'), salt).decode('utf-8')

    cur.execute("""
        INSERT INTO auth.user (id, email, password_hash, first_name, last_name, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """, (
        superuser_id,
        superuser_data['email'],
        password_hash,
        superuser_data.get('first_name'),
        superuser_data.get('last_name'),
        now,
        now
    ))
    cur.execute("""
        INSERT INTO auth.user_role (user_id, role_id) VALUES (%s, %s);
    """, (superuser_id, superuser_role_id))
    conn.commit()

    yield superuser_id

    if superuser_id:
        cur.execute("""
            DELETE FROM auth.login_history WHERE user_id = %s;
        """, (superuser_id,))
        cur.execute("""
            DELETE FROM auth.refresh_token WHERE user_id = %s;
        """, (superuser_id,))
        cur.execute("""
            DELETE FROM auth.user_role WHERE user_id = %s;
        """, (superuser_id,))
        cur.execute("""
            DELETE FROM auth.user WHERE id = %s;
        """, (superuser_id,))
        cur.execute("""
            DELETE FROM auth.role WHERE id = %s;
        """, (superuser_role_id,))

    conn.commit()
    cur.close()
    conn.close()
