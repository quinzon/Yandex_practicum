import pytest
from unittest.mock import AsyncMock, patch
from fastapi import Request
from auth_service.src.services.oauth import OAuthService


@pytest.fixture
def oauth_client():
    client = AsyncMock()
    return client


@pytest.fixture
def oauth_service(oauth_client):
    return OAuthService(oauth_client=oauth_client)


@pytest.fixture
def mock_request():
    return AsyncMock(spec=Request)