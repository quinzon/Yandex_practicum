import uuid
from datetime import datetime

review_create_data = {
    'user_id': 'user123',
    'film_id': str(uuid.uuid4()),
    'review_text': 'This is a sample review. The film was great!',
    'rating': 8
}

review_update_data = {
    'review_text': 'Updated review text. The film is still great, but with new insights!',
    'rating': 9
}

review_response_data = {
    'id': str(uuid.uuid4()),
    'user_id': 'user123',
    'film_id': 'film456',
    'review_text': 'This is a sample review. The film was great!',
    'rating': 8,
    'likes_count': 5,
    'dislikes_count': 1,
    'timestamp': datetime.utcnow().isoformat() + 'Z'
}

paginated_reviews_data = {
    'total': 1,
    'items': [review_response_data]
}

search_request_data = {
    'filters': {'film_id': 'film456'},
    'skip': 0,
    'limit': 10,
    'sort_by': 'timestamp',
    'sort_order': -1
}

reaction_request_data = {
    'reaction': 'like'
}
