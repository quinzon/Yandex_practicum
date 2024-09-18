import uuid

es_movies_data = [{
    'id': str(uuid.uuid4()),
    'imdb_rating': 8.5,
    'genres': [
        {'id': str(uuid.uuid4()), 'name': 'Action'},
        {'id': str(uuid.uuid4()), 'name': 'Sci-Fi'}
    ],
    'title': 'The Star',
    'description': 'New World',
    'directors': [
        {'id': str(uuid.uuid4()), 'full_name': 'Stan'}
    ],
    'actors_names': ['Ann', 'Bob'],
    'writers_names': ['Ben', 'Howard'],
    'actors': [
        {'id': str(uuid.uuid4()), 'full_name': 'Ann'},
        {'id': str(uuid.uuid4()), 'full_name': 'Bob'}
    ],
    'writers': [
        {'id': str(uuid.uuid4()), 'full_name': 'Ben'},
        {'id': str(uuid.uuid4()), 'full_name': 'Howard'}
    ]
} for _ in range(60)]
