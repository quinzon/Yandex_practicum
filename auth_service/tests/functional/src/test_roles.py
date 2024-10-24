import uuid
from http import HTTPStatus

import pytest

from auth_service.tests.functional.testdata.authorization import (role, already_exist_role, roles, new_role,
                                                                  permissions, already_exist_superuser)

pytestmark = pytest.mark.asyncio
ENDPOINT = '/api/v1/auth/roles'


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
async def test_create_role(make_post_request, setup_superuser, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    response_body, _, status = await make_post_request(
        f'{ENDPOINT}',
        json=role,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert 'id' in response_body


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [[already_exist_role]], indirect=True)
async def test_create_already_exist_role(make_post_request, make_get_request, setup_superuser, setup_roles, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    response_body, headers, status = await make_post_request(
        f'{ENDPOINT}',
        json=already_exist_role,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.CONFLICT


@pytest.mark.parametrize('setup_user', [already_exist_superuser], indirect=True)
async def test_create_role_without_access(make_post_request, setup_user, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    _, _, status = await make_post_request(
        f'{ENDPOINT}',
        json=role,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.FORBIDDEN


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [[already_exist_role]], indirect=True)
async def test_get_role(make_get_request, setup_superuser, setup_roles, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    role_ids = setup_roles

    response_body, _, status = await make_get_request(
        f'{ENDPOINT}/{role_ids[0]}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert response_body['name'] == already_exist_role['name']


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
async def test_get_non_existent_role(make_get_request, setup_superuser, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    role_id = str(uuid.uuid4())

    _, _, status = await make_get_request(
        f'{ENDPOINT}/{role_id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [[already_exist_role]], indirect=True)
async def test_update_role(make_put_request, setup_superuser, setup_roles, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    role_ids = setup_roles

    response_body, _, status = await make_put_request(
        f'{ENDPOINT}/{role_ids[0]}',
        json=new_role,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert response_body['name'] == new_role['name']


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
async def test_update_not_exist_role(make_put_request, setup_superuser, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    role_id = str(uuid.uuid4())

    response_body, _, status = await make_put_request(
        f'{ENDPOINT}/{role_id}',
        json=new_role,
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [[already_exist_role]], indirect=True)
async def test_delete_role(make_delete_request, setup_superuser, setup_roles, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    role_ids = setup_roles

    _, _, status = await make_delete_request(
        f'{ENDPOINT}/{role_ids[0]}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
async def test_delete_not_exist_role(make_delete_request, setup_superuser, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    role_id = str(uuid.uuid4())

    _, _, status = await make_delete_request(
        f'{ENDPOINT}/{role_id}',
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [roles], indirect=True)
async def test_get_roles(make_get_request, setup_superuser, setup_roles, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    response_body, _, status = await make_get_request(
        f'{ENDPOINT}',
        headers={'Authorization': f'Bearer {access_token}'},
    )

    assert status == HTTPStatus.OK
    assert isinstance(response_body['items'], list)
    assert len(response_body) >= len(roles)

    response_role_names = [r['name'] for r in response_body['items']]
    assert any(r['name'] in response_role_names for r in roles)


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [[already_exist_role]], indirect=True)
@pytest.mark.parametrize('setup_permissions', [permissions], indirect=True)
async def test_set_permissions_for_role(make_put_request, setup_superuser, setup_roles, setup_permissions, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    role_ids = setup_roles
    permission_ids = setup_permissions

    response_body, _, status = await make_put_request(
        f'{ENDPOINT}/{role_ids[0]}/permissions',
        json={'permission_ids': permission_ids},
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.OK
    assert response_body['id'] == role_ids[0]
    assert any([permission['id'] in permission_ids for permission in response_body['permissions']])


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
@pytest.mark.parametrize('setup_roles', [[already_exist_role]], indirect=True)
async def test_set_not_exist_permissions_for_role(make_put_request, setup_superuser, setup_roles, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    role_ids = setup_roles
    permission_ids = [str(uuid.uuid4())]

    _, _, status = await make_put_request(
        f'{ENDPOINT}/{role_ids[0]}/permissions',
        json={'permission_ids': permission_ids},
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize('setup_superuser', [already_exist_superuser], indirect=True)
async def test_set_permissions_for_not_exist_role(make_put_request, setup_superuser, get_tokens):
    access_token, _ = await get_tokens(already_exist_superuser['email'], already_exist_superuser['password'])

    role_id = str(uuid.uuid4())
    permission_ids = [str(uuid.uuid4())]

    _, _, status = await make_put_request(
        f'{ENDPOINT}/{role_id}/permissions',
        json={'permission_ids': permission_ids},
        headers={'Authorization': f'Bearer {access_token}'}
    )

    assert status == HTTPStatus.NOT_FOUND
