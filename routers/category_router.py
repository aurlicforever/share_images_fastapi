from fastapi import APIRouter, Depends,status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from core.dependencies import get_repository_wrapper
from schemas.response_model import ResponseModel
from core.logger import get_logger
from repositories.repository_wrapper import RepositoryWrapper

router = APIRouter(
    prefix="/api/categories",
    tags=["category"]
)
logger = get_logger()

@router.get("", response_model=ResponseModel)
async def get_categories(repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        categories_list = await repositories.category.get_categories()
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content= jsonable_encoder(ResponseModel(
                success=True, 
                data=categories_list, 
                message=f"Returned all categories from database."
            ))
        )

    except Exception as ex:
        logger.error(f"Something went wrong inside get_categories function: {ex}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(ResponseModel(success=False, message=f"Internal server error"))
        )