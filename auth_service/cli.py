import psycopg2
import typer
from passlib.context import CryptContext
from psycopg2.extras import DictCursor

from auth_service.src.core.config import PostgresSettings

app = typer.Typer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_superuser_in_db(email: str, password: str, db_conn_str: str):
    conn = psycopg2.connect(db_conn_str)
    cursor = conn.cursor(cursor_factory=DictCursor)

    try:
        cursor.execute("SELECT id FROM auth.role WHERE name = %s", ('superuser',))
        role = cursor.fetchone()

        if not role:
            cursor.execute(
                "INSERT INTO auth.role (id, name) VALUES (gen_random_uuid(), %s) RETURNING id",
                ('superuser',))
            role_id = cursor.fetchone()['id']
            conn.commit()
            typer.echo(f"Role 'superuser' created with id {role_id}")
        else:
            role_id = role['id']

        cursor.execute("SELECT id FROM auth.user WHERE email = %s", (email,))
        user = cursor.fetchone()

        if not user:
            password_hash = get_password_hash(password)
            cursor.execute(
                """INSERT INTO auth.user (id, email, password_hash, first_name, last_name, created_at, updated_at)
                VALUES (gen_random_uuid(), %s, %s, %s, %s, NOW(), NOW()) RETURNING id""",
                (email, password_hash, 'Super', 'Admin')
            )
            user_id = cursor.fetchone()['id']
            conn.commit()
            typer.echo(f"Superuser {email} created with id {user_id}")
        else:
            user_id = user['id']
            typer.echo(f"Superuser with email {email} already exists.")

        cursor.execute("SELECT 1 FROM auth.user_role WHERE user_id = %s AND role_id = %s",
                       (user_id, role_id))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO auth.user_role (user_id, role_id) VALUES (%s, %s)",
                           (user_id, role_id))
            conn.commit()
            typer.echo(f"Role 'superuser' assigned to {email}")

    except Exception as e:
        conn.rollback()
        typer.echo(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()


@app.command()
def create_superuser(email: str, password: str):
    pg_settings = PostgresSettings()
    db_conn_str = pg_settings.database_url.replace('+asyncpg', '')
    typer.echo(f"Creating superuser with email {email}")
    create_superuser_in_db(email, password, db_conn_str)


if __name__ == "__main__":
    app()
