from functools import lru_cache
from http import HTTPStatus

import httpx
from fastapi import HTTPException

from ugc_service.src.core.config import settings


class AuthServiceClient:
    def __init__(self):
        self.service_url = settings.auth_service_url

    async def check_permission(self, token: str, resource: str, http_method: str) -> bool:
        headers = {'Authorization': f'Bearer {token}'}
        params = {'resource': resource, 'http_method': http_method}

        async with httpx.AsyncClient() as client:
            response = await client.get(self.service_url, headers=headers, params=params)

            if response.status_code == HTTPStatus.OK:
                return True
            elif response.status_code == HTTPStatus.FORBIDDEN:
                return False
            else:
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail='Failed to communicate with auth service'
                )


@lru_cache()
def get_auth_service_client() -> AuthServiceClient:
    return AuthServiceClient()
