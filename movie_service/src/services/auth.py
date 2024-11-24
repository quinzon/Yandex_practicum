import aiohttp
from http import HTTPStatus
from functools import lru_cache

from fastapi import HTTPException

from movie_service.src.core.config import AUTH_SERVICE_URL


class AuthService:
    AUTH_SERVICE_URL = AUTH_SERVICE_URL

    async def check_permission(self, token: str, resource: str, http_method: str) -> bool | None:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.AUTH_SERVICE_URL}/users/check-permission",
                    params={"resource": resource, "http_method": http_method},
                    headers={'Authorization': token}
                ) as response:
                    if response.status == HTTPStatus.OK:
                        return True
                    raise HTTPException(
                        status_code=response.status,
                        detail="Authorization service error"
                    )
            except aiohttp.ClientError:
                raise HTTPException(
                    status_code=HTTPStatus.SERVICE_UNAVAILABLE,
                    detail="Authorization service connection error"
                )


@lru_cache()
def get_auth_service() -> AuthService:
    return AuthService()
