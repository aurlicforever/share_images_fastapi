from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from core.dependencies import get_db, get_repository_wrapper
from models.app_user import AppUser
from schemas.token_schema import TokenModel
from core.config import settings
from repositories.user_repository import UserRepository
from services.token_service import (
    generate_access_token,
    generate_refresh_token,
    get_principal_from_expired_token
)
from core.logger import get_logger
from datetime import datetime, timedelta, timezone
from schemas.response_model import ResponseModel
from core.api_key_header_middleware import get_current_user
from repositories.repository_wrapper import RepositoryWrapper

router = APIRouter(
    prefix="/api/token",
    tags=["token"]
)
logger = get_logger()

@router.post("/refresh")
async def refresh(token_model: TokenModel = Body(...), repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    if token_model is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(ResponseModel(success=False, message="Invalid client request")))


    access_token = token_model.token
    refresh_token = token_model.refresh_token
    principal = get_principal_from_expired_token(access_token)
    username = principal.get("sub")

    user = await repositories.user.get_user_by_email(username)

    if user.refresh_token_expiry_time.tzinfo is None:
        user.refresh_token_expiry_time = user.refresh_token_expiry_time.replace(tzinfo=timezone.utc)
    
    if user is None or user.refresh_token != refresh_token or user.refresh_token_expiry_time <= datetime.now(timezone.utc):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder(
                ResponseModel(success=False, message="Invalid client request")))

    new_access_token = generate_access_token(principal)
    new_refresh_token = generate_refresh_token()
    user.refresh_token = new_refresh_token
    user.refresh_token_expiry_time = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await repositories.user.update(user)

    token_data = TokenModel(token=new_access_token, refresh_token=new_refresh_token)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=jsonable_encoder(ResponseModel(
            success=True, message="Refresh successfully!", data=token_data)))

@router.post("/revoke", response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def revoke(current_user: AppUser = Depends(get_current_user),repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    user = await repositories.user.get_user_by_email(current_user.email)
    
    if user is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=jsonable_encoder(ResponseModel(success=False, message="Invalid client request"))
        )
    
    user.token = None
    await repositories.user.update_user(user)
    
    return None
