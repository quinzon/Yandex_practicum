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


# Тест успешного получения OAuth клиента
@pytest.mark.asyncio
async def test_get_oauth_client_success(oauth_service):
    with patch.object(oauth_service.oauth_client, 'create_client', return_value=AsyncMock()) as mock_create_client:
        client = await oauth_service.get_oauth_client('yandex')
        assert client is not None
        mock_create_client.assert_called_once_with('yandex')


# Тест авторизации через access token
@pytest.mark.asyncio
async def test_authorize_access_token(oauth_service, mock_request):
    mock_token = {'access_token': 'valid_token'}
    with patch.object(oauth_service, 'get_oauth_client', return_value=AsyncMock(authorize_access_token=AsyncMock(return_value=mock_token))) as mock_get_client:
        token_response = await oauth_service.authorize_access_token('yandex', mock_request)
        assert token_response == mock_token
        mock_get_client.assert_called_once_with('yandex')


# Тест получения информации о пользователе
@pytest.mark.asyncio
async def test_get_user_info(oauth_service):
    mock_token = {'access_token': 'valid_token'}
    expected_user_info = {
        'email': 'user@example.com',
        'name': 'Test User'
    }
    mock_client = AsyncMock(userinfo=AsyncMock(return_value=expected_user_info))
    with patch.object(oauth_service, 'get_oauth_client', return_value=mock_client) as mock_get_client:
        user_info = await oauth_service.get_user_info('yandex', mock_token)
        assert user_info == expected_user_info
        mock_get_client.assert_called_once_with('yandex')
        mock_client.userinfo.assert_called_once_with(token=mock_token)


# Тест на невалидный токен
@pytest.mark.asyncio
async def test_invalid_access_token(oauth_service, mock_request):
    mock_token = {'access_token': 'invalid_token'}
    with patch.object(oauth_service, 'authorize_access_token', side_effect=Exception("Invalid token")) as mock_authorize:
        with pytest.raises(Exception, match="Invalid token"):
            await oauth_service.authorize_access_token('yandex', mock_request)
        mock_authorize.assert_called_once_with(mock_request)


# Тест на ошибку при получении информации о пользователе
@pytest.mark.asyncio
async def test_get_user_info_failure(oauth_service):
    mock_token = {'access_token': 'valid_token'}
    with patch.object(oauth_service, 'get_oauth_client', return_value=AsyncMock(userinfo=AsyncMock(side_effect=Exception("Failed to get user info")))) as mock_get_client:
        with pytest.raises(Exception, match="Failed to get user info"):
            await oauth_service.get_user_info('yandex', mock_token)
        mock_get_client.assert_called_once_with('yandex')


# Тест на пустой токен
@pytest.mark.asyncio
async def test_empty_token(oauth_service):
    mock_token = {}
    with patch.object(oauth_service, 'get_oauth_client', return_value=AsyncMock(userinfo=AsyncMock(return_value={}))) as mock_get_client:
        user_info = await oauth_service.get_user_info('yandex', mock_token)
        assert user_info == {}
        mock_get_client.assert_called_once_with('yandex')


# Тест на неверный провайдер
@pytest.mark.asyncio
async def test_unsupported_provider(oauth_service):
    with pytest.raises(ValueError, match="Unsupported provider: unknown_provider"):
        await oauth_service.get_oauth_client('unknown_provider')
