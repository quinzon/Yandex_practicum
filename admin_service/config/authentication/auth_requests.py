from http import HTTPStatus

import requests

from django.core.exceptions import PermissionDenied, ValidationError
from django.conf import settings


AUTH_SERVICE_URL = settings.AUTH_SERVICE_URL


def check_permission(access_token: str, resource: str, http_method: str) -> bool:
    """Проверяет разрешение пользователя через auth-сервис."""
    response = requests.get(
        f'{AUTH_SERVICE_URL}/users/check-permission',
        params={'resource': resource, 'http_method': http_method},
        headers={'Authorization': f'Bearer {access_token}'},
    )
    return response.status_code == HTTPStatus.OK


def refresh_tokens(refresh_token: str) -> tuple[str | None, str | None]:
    """Обновляет токены через auth-сервис."""
    response = requests.post(
        f'{AUTH_SERVICE_URL}/refresh',
        headers={
            'accept': 'application/json',
            'Content-Type': 'application/json'
        },
        json={'refresh_token': refresh_token}
    )
    if response.status_code != HTTPStatus.OK:
        raise PermissionDenied('Ошибка обновления токенов.')

    data = response.json()
    return data.get('access_token'), data.get('refresh_token')


def login_user(email: str, password: str) -> dict:
    """Выполняет авторизацию пользователя через auth-сервис."""
    response = requests.post(
        f'{AUTH_SERVICE_URL}/login',
        headers={
            "accept": "application/json",
            "Content-Type": "application/json"
        },
        json={"email": email, "password": password}
    )
    if response.status_code != HTTPStatus.OK:
        detail = "Неизвестная ошибка" if response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR \
            else response.json().get('detail')
        raise ValidationError(f"Ошибка подключения к сервису авторизации: {response.status_code} - {detail}")

    return response.json()


def get_user_profile(access_token: str) -> dict:
    """Получает профиль пользователя через auth-сервис."""
    response = requests.get(
        f'{AUTH_SERVICE_URL}/users/profile',
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if response.status_code != HTTPStatus.OK:
        raise PermissionDenied('Ошибка получения профиля.')

    return response.json()
