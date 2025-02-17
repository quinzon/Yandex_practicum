from authlib.integrations.starlette_client import OAuth
from fastapi import Request

from auth_service.src.core.oauth import oauth


class OAuthService:
    def __init__(self, oauth_client: OAuth):
        self.oauth_client = oauth_client

    async def get_oauth_client(self, provider_name: str):
        client = self.oauth_client.create_client(provider_name)
        if not client:
            raise ValueError(f'Unsupported provider: {provider_name}')
        return client

    async def authorize_access_token(self, provider_name: str, request: Request):
        client = await self.get_oauth_client(provider_name)
        return await client.authorize_access_token(request)

    async def get_user_info(self, provider_name: str, token):
        client = await self.get_oauth_client(provider_name)
        return await client.userinfo(token=token)


def get_oauth_service() -> OAuthService:
    return OAuthService(oauth)
