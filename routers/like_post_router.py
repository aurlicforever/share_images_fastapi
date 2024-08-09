from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, Path, Header, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from schemas.response_model import ResponseModel
from schemas.like_post_schema import LikePostSchema, LikePostCreateSchema
from core.logger import get_logger
from core.api_key_header_middleware import get_api_key, get_current_user
from repositories.like_post_repository import LikePostRepository
from models.app_user import AppUser
from hashids import Hashids
from core.config import settings
from models.like_post import LikePost
from core.dependencies import get_repository_wrapper
from repositories.repository_wrapper import RepositoryWrapper

router = APIRouter(
    prefix="/api",
    tags=["likePost"]
)
logger = get_logger()

@router.get("/post/{post_id}/countPostLike", response_model=ResponseModel)
async def count_post_like(post_id: int,
                         repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        count_post_like = await repositories.like_post.count_post_likes(post_id)
        logger.info(f"Returned {count_post_like} Likes from database.")

        response_model = ResponseModel(
            success=True,
            data=count_post_like,
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(response_model)
        )

    except Exception as ex:
        logger.error(f"Something went wrong inside CountPostLike action: {ex}")
        response_model = ResponseModel(
            success=False,
            message="Internal server error"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(response_model)
        )
    
@router.post("/likePost/create", response_model=ResponseModel)
async def create_like_post(
    like_post: LikePostCreateSchema,
    repositories: RepositoryWrapper = Depends(get_repository_wrapper),
    current_user: AppUser = Depends(get_current_user)
):
    try:
        like_post = jsonable_encoder(like_post)
        if not like_post:
            logger.error("Likepost object sent from client is null.")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(
                    ResponseModel(success=False, message="Please fill in all fields!"))
            )
        
        hashids = Hashids(salt= settings.SALT, min_length=settings.HASHLENGTH)
        post_id = hashids.decode(like_post["postId"])[0]
        
        if not like_post["isLiked"]:
            old_like_post = await repositories.like_post.get_post_user_like(current_user.id, post_id)
            if old_like_post:
                await repositories.like_post.delete_like(old_like_post)
                logger.error("Like post has been deleted.")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=jsonable_encoder(
                        ResponseModel(success=True, message="Like post removed successfully", data=""))
                )
        else:
            like_post_entity = LikePost(
                post_id=post_id,
                user_id=current_user.id,
                is_liked=like_post["isLiked"],
                created_by=current_user.id,
            )
            await repositories.like_post.create_like(like_post_entity)
            return JSONResponse(
                status_code=status.HTTP_201_CREATED,
                content=jsonable_encoder(
                    ResponseModel(success=True, message="Like created successfully", data=""))
            )
        
    except Exception as ex:
        logger.error(f"Something went wrong inside Create Like post action: {ex}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(ResponseModel(success=False, message="Internal server error"))
        )

@router.get("/post/{post_id}/getPostUserLike", response_model=ResponseModel)
async def get_post_user_like(post_id: int, current_user: AppUser = Depends(get_current_user),
                            repositories: RepositoryWrapper = Depends(get_repository_wrapper),):
    try:
        like_post = await repositories.like_post.get_post_user_like(current_user.id, post_id)
        
        logger.info(f"Returned User {current_user.id} Likes for {post_id} from database.")
        
        response = jsonable_encoder(ResponseModel(success=True, data=like_post))
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)

    except Exception as ex:
        logger.error(f"Something went wrong inside get_post_user_like function: {ex}")
        response = jsonable_encoder(ResponseModel(success=False, message="Internal server error"))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response)