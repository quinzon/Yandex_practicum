from functools import wraps
from http import HTTPStatus

from fastapi import Request, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from auth_service.src.models.dto.common import ErrorMessages
from auth_service.src.services.access_control import AccessControlService, \
    get_access_control_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/login')


def has_permission():
    def decorator(func):
        @wraps(func)
        async def wrapper(
                token: str = Depends(oauth2_scheme),
                access_control_service: AccessControlService = Depends(get_access_control_service),
                *args, **kwargs
        ):
            request = kwargs.get('request', None)
            http_method = request.method
            resource = request.url.path

            has_permission_ = await access_control_service.check_permission(token, resource,
                                                                            http_method)
            if not has_permission_:
                raise HTTPException(
                    status_code=HTTPStatus.FORBIDDEN,
                    detail=ErrorMessages.PERMISSION_DENIED
                )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator
