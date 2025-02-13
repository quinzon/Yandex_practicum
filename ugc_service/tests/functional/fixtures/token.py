import pytest
import base64
import json
from datetime import datetime, timedelta

def base64_url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

def generate_token(user_id: str = 'user123', email: str = 'user123@example.com', roles: list[str] = None) -> str:
    if roles is None:
        roles = ['user']
    header = {'alg': 'HS256', 'typ': 'JWT'}
    payload = {
        'sub': user_id,
        'email': email,
        'roles': roles,
        'exp': int((datetime.utcnow() + timedelta(minutes=30)).timestamp())
    }

    encoded_header = base64_url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    encoded_payload = base64_url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    token = f'{encoded_header}.{encoded_payload}.dummy_signature'
    return token

@pytest.fixture
def token_factory():
    def _factory(user_id='user123', email='user123@example.com', roles=None) -> str:
        res = generate_token(user_id=user_id, email=email, roles=roles)
        print(res)
        print(user_id, email, roles)
        return res
    return _factory

@pytest.fixture
def valid_token(token_factory):
    return token_factory()
