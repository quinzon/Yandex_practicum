import uuid

import pytest
from http import HTTPStatus

from auth_service.tests.functional.testdata.authentication import valid_user, valid_login
from auth_service.tests.functional.testdata.authorization import already_exist_role, roles, \
    already_exist_superuser, already_exist_user, permission

pytestmark = pytest.mark.asyncio
ENDPOINT = '/api/v1/auth/users'


# Test for getting user profile
async def test_get_profile(make_get_request, get_tokens):
    # Get valid tokens
    access_token, _ = await get_tokens(valid_login['email'], valid_login['password'])

    # Send a request to get the profile
    response_body, headers, status = await make_get_request(
        f'{ENDPOINT}/profile',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert response_body['email'] == valid_user['email']
    assert response_body['first_name'] == valid_user['first_name']
    assert response_body['last_name'] == valid_user['last_name']
    assert response_body['patronymic'] == valid_user['patronymic']


# Test for getting login history
async def test_get_login_history_with_pagination(make_get_request, get_tokens):
    access_token, _ = await get_tokens(valid_login['email'], valid_login['password'])

    page_size = 10
    page_number = 1

    response_body, headers, status = await make_get_request(
        f'{ENDPOINT}/profile/login-history',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'page_size': page_size, 'page_number': page_number}
    )

    assert status == HTTPStatus.OK

    # check response structure
    assert 'meta' in response_body
    assert 'items' in response_body

    meta = response_body['meta']
    items = response_body['items']

    # check paging attributes
    assert meta['page_size'] == page_size
    assert meta['page_number'] == page_number
    assert meta['total_items'] >= 0
    assert meta['total_pages'] >= 1

    # check items len
    assert isinstance(items, list)
    assert len(items) <= page_size

    # check we have entries
    assert len(items) > 0


# Test for updating user profile
async def test_update_profile(make_put_request, get_tokens):
    # Get valid tokens
    access_token, _ = await get_tokens(valid_login['email'], valid_login['password'])

    # Prepare new profile data
    update_data = {
        'first_name': 'UpdatedName',
        'last_name': 'UpdatedLastName',
        'patronymic': 'UpdatedPatronymic',
        'password': 'newStrongPassword123!'
    }

    # Send a request to update the profile
    response_body, headers, status = await make_put_request(
        f'{ENDPOINT}/profile',
        json=update_data,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert response_body['first_name'] == 'UpdatedName'
    assert response_body['last_name'] == 'UpdatedLastName'
    assert response_body['patronymic'] == 'UpdatedPatronymic'


# Test for invalid access token
async def test_get_profile_invalid_token(make_get_request):
    # Use an invalid token
    invalid_token = 'invalid_token'

    response_body, headers, status = await make_get_request(
        f'{ENDPOINT}/profile',
        headers={'Authorization': f'Bearer {invalid_token}'}
    )

    assert status == HTTPStatus.UNAUTHORIZED


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [roles], indirect=True)
async def test_set_roles_for_user(make_put_request, setup_superuser, setup_roles, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    user_id = setup_superuser
    role_names = setup_roles

    response_body, _, status = await make_put_request(
        f'{ENDPOINT}/{user_id}/roles',
        json={'role_names': role_names},
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert status == HTTPStatus.OK
    assert response_body['id'] == user_id
    assert any([r in [_['name'] for _ in roles] for r in response_body['roles']])


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [[already_exist_role]], indirect=True)
async def test_set_not_exist_roles_for_user(make_put_request, setup_superuser, setup_roles, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    user_id = setup_superuser
    role_names = [str(uuid.uuid4())]

    _, _, status = await make_put_request(
        f'{ENDPOINT}/{user_id}/permissions',
        json={'role_names': role_names},
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [[already_exist_role]], indirect=True)
async def test_set_roles_for_not_exist_user(make_put_request, setup_superuser, setup_roles, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    user_id = str(uuid.uuid4())
    role_names = setup_roles

    _, _, status = await make_put_request(
        f'{ENDPOINT}/{user_id}/permissions',
        json={'role_names': role_names},
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_user', [already_exist_user], indirect=True)
@pytest.mark.parametrize('setup_roles', [[already_exist_role]], indirect=True)
@pytest.mark.parametrize('setup_permissions', [[permission]], indirect=True)
async def test_check_permission(make_get_request, make_post_request, make_put_request, setup_superuser, setup_user,
                                setup_roles, setup_permissions, get_tokens):
    superuser_access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    user_id = setup_user
    role_names = setup_roles
    permission_ids = setup_permissions

    await make_put_request(
        f'/api/v1/auth/roles/{role_names[0]}/permissions',
        json={'permission_ids': permission_ids},
        headers={'Authorization': f'Bearer {superuser_access_token}'}
    )

    await make_put_request(
        f'{ENDPOINT}/{user_id}/roles',
        json={'role_names': role_names},
        headers={'Authorization': f'Bearer {superuser_access_token}'}
    )

    user_access_token, _ = await get_tokens(already_exist_user['email'], already_exist_user['password'])

    response_body, _, status = await make_get_request(
        f'{ENDPOINT}/check-permission',
        params={'resource': 'test_resource', 'http_method': 'post'},
        headers={'Authorization': f'Bearer {user_access_token}'}
    )

    assert status == HTTPStatus.OK


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [roles], indirect=True)
@pytest.mark.parametrize('setup_user', [already_exist_user], indirect=True)
@pytest.mark.asyncio
async def test_get_users(async_client, access_token):
    response = await async_client.get(
        f"{ENDPOINT}/users",
        params={"role_name": None, "page_size": 10, "page_number": 1},
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == HTTPStatus.OK

    response_json = response.json()

    assert isinstance(response_json, list)
