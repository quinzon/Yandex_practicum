import uuid
from http import HTTPStatus

import pytest

from auth_service.tests.functional.testdata.authorization import (already_exist_permission, new_permission, permissions,
                                                                  already_exist_superuser, permission)

pytestmark = pytest.mark.asyncio
ENDPOINT = '/api/v1/auth/permissions'


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
async def test_create_permission(make_post_request, setup_superuser, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    response_body, _, status = await make_post_request(
        f'{ENDPOINT}',
        json=permission,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert 'id' in response_body


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_permissions', [[already_exist_permission]], indirect=True)
async def test_create_already_exist_permission(make_post_request, make_get_request, setup_superuser, setup_permissions,
                                               get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    response_body, headers, status = await make_post_request(
        f'{ENDPOINT}',
        json=already_exist_permission,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.CONFLICT


@pytest.mark.parametrize('setup_user', [already_exist_superuser], indirect=True)
async def test_create_permission_without_access(make_post_request, setup_user, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    _, _, status = await make_post_request(
        f'{ENDPOINT}',
        json=permission,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.FORBIDDEN


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_permissions', [[already_exist_permission]], indirect=True)
async def test_get_permission(make_get_request, setup_superuser, setup_permissions, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    permission_ids = setup_permissions

    response_body, _, status = await make_get_request(
        f'{ENDPOINT}/{permission_ids[0]}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert response_body['name'] == already_exist_permission['name']


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
async def test_get_non_existent_permission(make_get_request, setup_superuser, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    permission_id = str(uuid.uuid4())

    _, _, status = await make_get_request(
        f'{ENDPOINT}/{permission_id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_permissions', [[already_exist_permission]], indirect=True)
async def test_update_permission(make_put_request, setup_superuser, setup_permissions, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    permission_ids = setup_permissions

    response_body, _, status = await make_put_request(
        f'{ENDPOINT}/{permission_ids[0]}',
        json=new_permission,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert response_body['name'] == new_permission['name']


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
async def test_update_not_exist_permission(make_put_request, setup_superuser, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    permission_id = str(uuid.uuid4())

    response_body, _, status = await make_put_request(
        f'{ENDPOINT}/{permission_id}',
        json=new_permission,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_permissions', [[already_exist_permission]], indirect=True)
async def test_delete_permission(make_delete_request, setup_superuser, setup_permissions, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    permission_ids = setup_permissions

    _, _, status = await make_delete_request(
        f'{ENDPOINT}/{permission_ids[0]}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
async def test_delete_not_exist_permission(make_delete_request, setup_superuser, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    permission_id = str(uuid.uuid4())

    _, _, status = await make_delete_request(
        f'{ENDPOINT}/{permission_id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_permissions', [permissions], indirect=True)
async def test_get_permissions(make_get_request, setup_superuser, setup_permissions, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    response_body, _, status = await make_get_request(
        f'{ENDPOINT}',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert status == HTTPStatus.OK
    assert isinstance(response_body['items'], list)
    assert len(response_body) >= len(permissions)

    response_permission_names = [p['name'] for p in response_body['items']]
    assert any(p['name'] in response_permission_names for p in permissions)
