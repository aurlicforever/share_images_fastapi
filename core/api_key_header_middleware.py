from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.api_key import APIKeyHeader
import jwt
from core.config import settings
from core.dependencies import get_repository_wrapper
from repositories.repository_wrapper import RepositoryWrapper
from services.token_service import decode_token

api_key_header = APIKeyHeader(name="X-Api-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key missing"
        )
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        user_email = decode_token(token).get("sub")
        user = await repositories.user.get_user_by_email(user_email)
        if user_email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
    except jwt.PyJWTError as ex:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail= f"{ex}"
            )

    user = await repositories.user.get_user_by_email(user_email)
    if user is None:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
    return user