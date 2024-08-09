from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import parse_obj_as
from database.database import get_db
from schemas.response_model import ResponseModel
from schemas.user_schema import UserSchema, UserUpdateSchema, UserParameters, validate_user_update
from core.api_key_header_middleware import get_current_user
from models.app_user import AppUser
from core.logger import get_logger
from repositories.repository_wrapper import RepositoryWrapper
from core.dependencies import get_repository_wrapper

router = APIRouter(
    prefix="/api/user",
    tags=["user"]
)
logger = get_logger()

@router.get("/users", response_model=ResponseModel)
async def get_users(user_parameters: UserParameters = Depends(),
                      repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        users_paged_list = await repositories.user.get_users(user_parameters)

        logger.info(f"Returned {users_paged_list.meta_data.total_count} users from database.")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content= jsonable_encoder(ResponseModel(
                success=True, 
                data=users_paged_list.items, 
                message=f"Returned {users_paged_list.meta_data.total_count} users from database."
            ))
        )

    except Exception as ex:
        logger.error(f"Something went wrong inside get_users function: {ex}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(ResponseModel(success=False, message=f"Internal server error {ex}"))
        )

@router.get("/{user_name}", name="User By Username")
async def get_user_by_user_name(user_name: str,
                                repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        user = await repositories.user.get_user_by_user_name(user_name)
        if not user:
            return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content=jsonable_encoder(ResponseModel(success=False, message= "User not found"))
                )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                ResponseModel(
                success=True, 
                data= UserSchema.from_orm(user)
                )
            )
        )

    except Exception as ex:
        logger.error(f"Something went wrong inside GetUserById action: {ex}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(ResponseModel(success=False, message=f"Internal server error {ex}"))
        )

@router.put("", name="Update User")
async def update_user(
    user_update_schema: UserUpdateSchema = Depends(UserUpdateSchema.as_form),
    current_user: AppUser = Depends(get_current_user),
    repositories: RepositoryWrapper = Depends(get_repository_wrapper)
):
    try:
        user_update_schema = jsonable_encoder(user_update_schema)
        user_update_schema = parse_obj_as(UserUpdateSchema, user_update_schema)

        # Update user details
        current_user.name = user_update_schema.name
        current_user.user_name = user_update_schema.user_name
        current_user.country_id = user_update_schema.country_id

        await repositories.user.update(current_user)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                ResponseModel(
                    success=True,
                    message="User updated successfully!",
                    data=UserSchema.from_orm(current_user)
                )
            )
        )

    except Exception as ex:
        logger.error(f"Something went wrong inside Update User action: {ex}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(ResponseModel(success=False, message=f"Internal server error"))
        )