import uuid


es_film_data = {
    'id': str(uuid.uuid4()),
    'title': 'The Star',
    'imdb_rating': 8.5,
    'description': 'New World',
    'genres': [
        {
            'id': str(uuid.uuid4()),
            'name': str(uuid.uuid4()),
            'description': str(uuid.uuid4())
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Sci-Fi',
            'description': str(uuid.uuid4())
        }
    ],
    'directors': [
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Stan'
        }
    ],
    'actors': [
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Ann'
        },
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Bob'
        }
    ],
    'writers': [
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Ben'
        },
        {
            'id': str(uuid.uuid4()),
            'full_name': 'Howard'
        }
    ]
}

es_films_data = [es_film_data for _ in range(60)]
