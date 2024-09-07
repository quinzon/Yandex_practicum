COMMON_MOVIE_SQL = """
    SELECT
       fw.id,
       fw.title,
       fw.description,
       fw.rating,
       fw.type,
       fw.updated_at,
       COALESCE (
           json_agg(
               DISTINCT jsonb_build_object(
                   'person_role', pfw.role,
                   'person_id', p.id,
                   'person_name', p.full_name
               )
           ) FILTER (WHERE p.id is not null),
           '[]'
       ) as persons,
       array_agg(DISTINCT g.name) as genres"""

MOVIES_SQL_BY_MODIFIED_MOVIES = COMMON_MOVIE_SQL + """
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
    WHERE (fw.updated_at > %s) or (fw.updated_at = %s and fw.id > %s) 
    GROUP BY fw.id
    ORDER BY fw.updated_at, fw.id;
    """

MOVIES_SQL_BY_MODIFIED_GENRES = COMMON_MOVIE_SQL + """
    FROM content.genre g
    LEFT JOIN content.genre_film_work gfw ON gfw.genre_id = g.id
    LEFT JOIN content.film_work fw ON fw.id = gfw.film_work_id
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    WHERE (g.updated_at > %s) or (g.updated_at = %s and fw.id > %s)
    GROUP BY fw.id
    ORDER BY MAX(g.updated_at), fw.id;
    """

MOVIES_SQL_BY_MODIFIED_PERSONS = COMMON_MOVIE_SQL + """
    FROM content.person p
    LEFT JOIN content.person_film_work pfw ON pfw.person_id = p.id
    LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
    WHERE (p.updated_at > %s) or (p.updated_at = %s and fw.id > %s)
    GROUP BY fw.id
    ORDER BY MAX(p.updated_at), fw.id;
    """
