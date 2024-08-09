from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import parse_obj_as
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.comment_repository import CommentRepository
from schemas.response_model import ResponseModel
from schemas.comment_schema import CommentCreateSchema, CommentParameters, CommentSchema
from models.comment import Comment
from models.app_user import AppUser
from hashids import Hashids
from core.config import settings
from core.api_key_header_middleware import get_current_user
from database.database import get_db
from core.dependencies import get_repository_wrapper
from repositories.repository_wrapper import RepositoryWrapper
from core.logger import get_logger

router = APIRouter(
    prefix="/api",
    tags=["comment"]
)
logger = get_logger()

@router.get("/post/{post_hash_id}/countComments", response_model=ResponseModel)
async def count_comments(post_hash_id: str, repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        hashids = Hashids(settings.SALT, settings.HASHLENGTH)
        post_id = hashids.decode(post_hash_id)[0]
        count = await repositories.comment.count_comments(post_id)
        logger.info(f"Returned {count} Comments from database.")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(ResponseModel(success=True, data=count))
        )
    except Exception as ex:
        logger.error(f"Something went wrong inside CountComments action: {ex}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ResponseModel(success=False, message="Internal server error")
            )
        )

@router.post("/comment", response_model=ResponseModel)
async def create_comment(
    comment: CommentCreateSchema,
    repositories: RepositoryWrapper = Depends(get_repository_wrapper),
    current_user: AppUser = Depends(get_current_user)
):
    try:
        if not comment:
            logger.error("Comment object sent from client is null.")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content=jsonable_encoder(
                    ResponseModel(
                        success=False, message="Please fill in all fields!")
                )
            )
        comment = jsonable_encoder(comment)
        comment = parse_obj_as(CommentCreateSchema, comment)
        comment_entity = Comment(
            post_id = comment.post_id,
            user_id = current_user.id,
            created_by = current_user.id,
            comment_text = comment.comment_text
        )
        created_comment = await repositories.comment.create_comment(comment_entity)
        created_comment = await repositories.comment.get_comment_by_id(created_comment.id)
        comment_schema = CommentSchema.from_orm(created_comment)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content=jsonable_encoder(
                ResponseModel(success=True, message="Comment created successfully!", 
                                  data=comment_schema))
                                  )
    except Exception as ex:
        logger.error(f"Something went wrong inside Create Comment action: {ex}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(
                ResponseModel(success=False, message="Internal server error")))

@router.get("/post/{post_hash_id}/comments", response_model=ResponseModel)
async def get_post_comments(
    post_hash_id: str,
    commentParameters: CommentParameters = Depends(),
    repositories: RepositoryWrapper = Depends(get_repository_wrapper)
):
    try:
        hashids = Hashids(settings.SALT, settings.HASHLENGTH)
        post_id = hashids.decode(post_hash_id)[0]
        comments_paged_list = await repositories.comment.get_post_comments(post_id, commentParameters)
        logger.info(f"Returned {comments_paged_list.meta_data.total_count} Comments from database.")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                ResponseModel(
                    success=True, 
                    data=comments_paged_list.items,
                    message=f"Returned {comments_paged_list.meta_data.total_count} comments from database."
                )))
    except Exception as ex:
        logger.error(f"Something went wrong inside GetpostComments action: {ex}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(ResponseModel(success=False, message="Internal server error"))
            )

@router.delete("/comment/{comment_id}", response_model=ResponseModel)
async def delete_comment(
    comment_id: int,
    repositories: RepositoryWrapper = Depends(get_repository_wrapper),
    current_user: AppUser = Depends(get_current_user)
):
    try:
        comment = await repositories.comment.get_comment_by_id(comment_id)
        if not comment:
            logger.error("Comment object sent from client is null.")
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=jsonable_encoder(
                    ResponseModel(success=False, message="Comment not found!"))
            )

        comment.is_active = False
        comment.is_deleted = True
        await repositories.comment.update_comment(comment)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(
                ResponseModel(success=True, message="Comment successfully deleted!")))
    except Exception as ex:
        logger.error(f"Something went wrong inside Delete Comment action: {ex}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=jsonable_encoder(ResponseModel(success=False, message="Internal server error")))
