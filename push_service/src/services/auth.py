import httpx
from functools import lru_cache
from fastapi import HTTPException

from push_service.src.core.config import get_global_settings

settings = get_global_settings()


class AuthService:
    AUTH_SERVICE_URL = settings.auth_service_url

    async def get_profile(self, auth_token: str) -> dict:
        auth_url = self.AUTH_SERVICE_URL

        async with httpx.AsyncClient() as client:
            response = await client.get(f'{auth_url}/users/profile', headers={'Authorization': auth_token})
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=response.status_code, detail='Get profile failed')

    async def get_user_id(self, auth_token: str) -> str:
        profile = await self.get_profile(auth_token)
        return profile.get('id')


@lru_cache()
def get_auth_service() -> AuthService:
    return AuthService()
