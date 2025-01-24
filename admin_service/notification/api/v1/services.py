from django.db import connection


def get_users_by_role(role, page=1, page_size=10):
    offset = (page - 1) * page_size

    with connection.cursor() as cursor:
        if role == 'all_users':
            cursor.execute("""
                SELECT email, first_name, last_name
                FROM auth.user
                LIMIT %s OFFSET %s;
            """, [page_size, offset])
        else:
            cursor.execute("""
                SELECT
                    u.email,
                    u.first_name,
                    u.last_name
                FROM
                    auth.user u
                LEFT JOIN
                    user_role ur ON u.id = ur.user_id
                LEFT JOIN
                    role r ON ur.role_id = r.id
                WHERE
                    r.name = %s
                LIMIT %s OFFSET %s;
            """, [role, page_size, offset])

        return cursor.fetchall()
