from datetime import datetime, timedelta

import pytest
import base64
import json

def generate_token(user_id: str, email: str = "test@example.com", roles: list = None) -> str:
    if roles is None:
        roles = ["user"]
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "email": email,
        "roles": roles,
        "exp": int((datetime.utcnow() + timedelta(minutes=30)).timestamp())
    }

    def base64_url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('utf-8')

    encoded_header = base64_url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    encoded_payload = base64_url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    # Сигнатура может быть фиктивной, так как проверка подписи не производится в тестах
    token = f"{encoded_header}.{encoded_payload}.dummy_signature"
    return token

@pytest.fixture
def valid_token():
    # Генерируем токен для пользователя с user_id "user123"
    return generate_token("user123", email="user123@example.com")
