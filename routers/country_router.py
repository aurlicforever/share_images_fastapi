from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path, Header, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from database.database import SessionLocal
from sqlalchemy.orm import Session
from repositories.user_repository import UserRepository
from repositories.country_repository import CountryRepository
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import get_db
from schemas.page_list_schema import PagedList
from core.sort_helper import SortHelper
from schemas.response_model import ResponseModel
from core.logger import get_logger
from schemas.user_schema import UserSchema
from core.api_key_header_middleware import get_api_key
from repositories.repository_wrapper import RepositoryWrapper
from core.dependencies import get_repository_wrapper

router = APIRouter(
    prefix="/api/countries",
    tags=["country"]
)
logger = get_logger()

@router.get("", response_model=ResponseModel)
async def get_countries(repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        countries_list = await repositories.country.get_countries()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content= jsonable_encoder(ResponseModel(
                success=True, 
                data=countries_list, 
                message=f"Returned all countries from database."
            ))
        )

    except Exception as ex:
        logger.error(f"Something went wrong inside get_countries function: {ex}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(ResponseModel(success=False, message=f"Internal server error"))
        )