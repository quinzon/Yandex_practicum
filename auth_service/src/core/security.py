from http import HTTPStatus

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError

from auth_service.src.models.dto.token import TokenData
from auth_service.src.services.token import TokenService, get_token_service
from auth_service.src.models.dto.common import ErrorMessages


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def require_token(token_service: TokenService = Depends(get_token_service)):
    async def verify_token(token: str = Depends(oauth2_scheme)) -> TokenData:
        try:
            token_data = await token_service.verify_token(token)
            return token_data
        except JWTError:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED,
                detail=ErrorMessages.INVALID_ACCESS_TOKEN
            )
    return Depends(verify_token)
