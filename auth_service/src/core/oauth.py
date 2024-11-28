from authlib.integrations.starlette_client import OAuth

from auth_service.src.core.config import get_oauth_settings

oauth = OAuth()


def register_providers():
    settings = get_oauth_settings()

    for provider_name, provider_settings in settings.providers.items():
        oauth.register(
            name=provider_name,
            client_id=provider_settings.client_id,
            client_secret=provider_settings.client_secret,
            authorize_url=provider_settings.authorize_url,
            access_token_url=provider_settings.access_token_url,
            client_kwargs={'scope': provider_settings.scope},
            userinfo_endpoint=provider_settings.userinfo_endpoint,
        )
