import base64
import json

from fastapi import Depends, Request, HTTPException
from fastapi.security import OAuth2PasswordBearer
from http import HTTPStatus

from ugc_service.src.services.auth import AuthServiceClient, get_auth_service_client

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


def get_user_id(token: str) -> dict:
    payload_part = token.split('.')[1]
    payload_decoded = base64.urlsafe_b64decode(payload_part + '=' * (-len(payload_part) % 4))
    return json.loads(payload_decoded).get('user_id', '')


async def has_permission(
        request: Request,
        token: str = Depends(oauth2_scheme),
        auth_service_client: AuthServiceClient = Depends(get_auth_service_client)
):
    http_method = request.method
    resource = request.url.path
    headers = request.headers

    has_access = await auth_service_client.check_permission(token, resource, http_method, headers)
    if not has_access:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail='Permission denied'
        )

    return get_user_id(token)
