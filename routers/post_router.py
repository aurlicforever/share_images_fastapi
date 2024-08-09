from datetime import datetime, timezone
import logging
from PIL import Image
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from jwt import PyJWTError
import jwt
from pydantic import parse_obj_as
from schemas.post_schema import PostCreateSchema, PostUpdateSchema, PostParameters, PostSchema, PostWithActionsCountSchema
from schemas.response_model import ResponseModel
from core.config import settings
from services.token_service import decode_token
from hashids import Hashids
from repositories.repository_wrapper import RepositoryWrapper
from core.dependencies import get_repository_wrapper
import logging
import os
import uuid
from core.api_key_header_middleware import get_current_user
from core.logger import get_logger
from models.post import Post
from models.app_user import AppUser

router = APIRouter(
    prefix="/api",
    tags=["post"]
)
logger = get_logger()

@router.get("/posts", response_model=ResponseModel, name="Posts")
async def get_all_posts(
    request: Request,
    post_parameters: PostParameters = Depends(),
    repositories: RepositoryWrapper = Depends(get_repository_wrapper)
):
    try:
        # Check if user is logged in
        token_with_bearer = request.headers.get("Authorization")
        user = None
        if token_with_bearer:
            token = token_with_bearer.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHHM])
                user_email = payload.get("sub")
                if user_email:
                    user = await repositories.user.get_user_by_email(user_email)
            except PyJWTError as e:
                logger.error(f"JWT error: {e}")
                # raise HTTPException(status_code=401, detail="Invalid token")


        posts_paged_list = await repositories.post.get_all_posts(post_parameters)
        logger.info(f"Returned {posts_paged_list.meta_data.total_count} posts from database.")

        list_post_with_actions_count = []
        for post in posts_paged_list.items:
            likes_count = await repositories.like_post.count_post_likes(post.id)
            comments_count = await repositories.comment.count_comments(post.id)
            current_user_like = False
            if user:
                user_like = await repositories.like_post.get_post_user_like(user.id, post.id)
                if user_like:
                    current_user_like = True
            
            post_with_actions_count = PostWithActionsCountSchema(
                post=PostSchema.from_orm(post),
                likes_count=likes_count,
                comments_count=comments_count,
                current_user_like=current_user_like
            )

            list_post_with_actions_count.append(post_with_actions_count)

        response_model = ResponseModel(
            success=True,
            message=posts_paged_list.meta_data.total_count,
            data=list_post_with_actions_count
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(response_model))

    except HTTPException as ex:
        logging.error(f"HTTP error in GetAllPosts action: {ex.detail}")
        response_model = ResponseModel(success=False, message=f"HTTP error: {ex.detail}")
        return JSONResponse(status_code=ex.status_code, content=jsonable_encoder(response_model))
    except Exception as ex:
        logging.error(f"Something went wrong inside GetAllPosts action: {ex}")
        response_model = ResponseModel(success=False, message=f"Internal server error {ex}")
        return JSONResponse(status_code=500, content=jsonable_encoder(response_model))

@router.get("/post/{hashid}", name="PostById")
async def get_post_by_id(
    hashid: str, request: Request, 
    repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        hashids = Hashids(settings.SALT, settings.HASHLENGTH)
        id = hashids.decode(hashid)[0]
        post = await repositories.post.get_post_by_id(id)
        if not post:
            response = jsonable_encoder(ResponseModel(success=False, message="Not found"))
            return JSONResponse(status_code=404, content=response)

        token_with_bearer = request.headers.get("Authorization")
        user = None
        if token_with_bearer:
            token = token_with_bearer.split(" ")[1]
            email = decode_token(token).get("sub")
            user = await repositories.user.get_user_by_email(email)
            

        likes_count = await repositories.like_post.count_post_likes(post.id)
        comment_count = await repositories.comment.count_comments(post.id)
        current_user_like = False
        if user is not None:
            user_like = await repositories.like_post.get_post_user_like(user.id, post.id)
            if user_like is not None:
                current_user_like = True

        post_with_actions_count = PostWithActionsCountSchema(
            post=PostSchema.from_orm(post),
            likes_count=likes_count,
            comments_count=comment_count,
            current_user_like=current_user_like
        )

        response = jsonable_encoder(ResponseModel(success=True, data=post_with_actions_count))
        return JSONResponse(status_code=200, content=response)
    except Exception as ex:
        response = ResponseModel(success=False, message=f"Internal server error {ex}")
        return JSONResponse(status_code=500, content=response)

@router.get("/post/user/{user_id}", name="UserPosts")
async def get_user_posts(user_id: int, 
                        request: Request, 
                        post_parameters: PostParameters = Depends(), 
                        repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        token_with_bearer = request.headers.get("Authorization")
        user = None
        if token_with_bearer:
            token = token_with_bearer.split(" ")[1]
            email = decode_token(token).get("sub")
            user = await repositories.user.get_user_by_email(email)
            if user is None:
                response = jsonable_encoder(
                    ResponseModel(success=False, message="This user does not exist!"))
                return JSONResponse(status_code=404, content=response)

        posts = await repositories.post.get_user_posts(user_id, post_parameters)
        list_post_with_actions_count = []
        for post in posts.items:
            likes_count = await repositories.like_post.count_post_likes(post.id)
            comment_count = await repositories.comment.count_comments(post.id)
            current_user_like = False
            if user is not None:
                user_like = await repositories.like_post.get_post_user_like(user.id, post.id)
                if user_like is not None:
                    current_user_like = True
            post_with_actions_count = PostWithActionsCountSchema(
                post=PostSchema.from_orm(post),
                likes_count=likes_count,
                comments_count=comment_count,
                current_user_like=current_user_like
            )
            list_post_with_actions_count.append(post_with_actions_count)

        response_model = jsonable_encoder(ResponseModel(
            success=True,
            message=posts.meta_data.total_count,
            data=list_post_with_actions_count
        ))
        return JSONResponse(status_code=200, content=jsonable_encoder(response_model))
    except Exception as ex:
        response = jsonable_encoder(ResponseModel(success=False, message=f"Internal server error {ex}"))
        return JSONResponse(status_code=500, content=response)  
    
@router.get("/posts/{category}", name="PostByCategory")
async def get_post_by_category(
    category: str, request: Request,
    post_parameters: PostParameters = Depends(),
    repositories: RepositoryWrapper = Depends(get_repository_wrapper)):
    try:
        category = await repositories.category.get_category_by_name(category)
        if not category:
            response = jsonable_encoder(ResponseModel(success=False, message="Category not found"))
            return JSONResponse(status_code=404, content=response)

        token_with_bearer = request.headers.get("Authorization")
        user = None
        if token_with_bearer:
            token = token_with_bearer.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHHM])
                user_email = payload.get("sub")
                if user_email:
                    user = await repositories.user.get_user_by_email(user_email)
            except PyJWTError as e:
                logger.error(f"JWT error: {e}")
                # raise HTTPException(status_code=401, detail="Invalid token")


        posts_paged_list = await repositories.post.get_post_by_category(category.id ,post_parameters)
        logger.info(f"Returned {posts_paged_list.meta_data.total_count} posts from database.")

        list_post_with_actions_count = []
        for post in posts_paged_list.items:
            likes_count = await repositories.like_post.count_post_likes(post.id)
            comments_count = await repositories.comment.count_comments(post.id)
            current_user_like = False
            if user:
                user_like = await repositories.like_post.get_post_user_like(user.id, post.id)
                if user_like:
                    current_user_like = True
            
            post_with_actions_count = PostWithActionsCountSchema(
                post=PostSchema.from_orm(post),
                likes_count=likes_count,
                comments_count=comments_count,
                current_user_like=current_user_like
            )

            list_post_with_actions_count.append(post_with_actions_count)

        response_model = ResponseModel(
            success=True,
            message=posts_paged_list.meta_data.total_count,
            data=list_post_with_actions_count
        )
        return JSONResponse(status_code=200, content=jsonable_encoder(response_model))
    except Exception as ex:
        response = ResponseModel(success=False, message=f"Internal server error {ex}")
        return JSONResponse(status_code=500, content=response)


@router.post("/post/upload", name="Upload Post", status_code=status.HTTP_200_OK)
async def upload_post(
    post_create_schema: PostCreateSchema = Depends(PostCreateSchema.as_form),
    file_image: UploadFile = File(None, alias='fileImage'),
    current_user: dict = Depends(get_current_user),
    repositories: RepositoryWrapper = Depends(get_repository_wrapper)
):
    try:
        post_create_schema = jsonable_encoder(post_create_schema)
        post_create_schema = parse_obj_as(PostCreateSchema, post_create_schema)

        user_email = current_user.email
        user = await repositories.user.get_user_by_email(user_email)
        if not user:
            response = jsonable_encoder(ResponseModel(success=False, message="The user does not exist!"))
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=response)

        destination_folder = os.path.join("assets", "post", user.folder)
        if file_image:
            image = Image.open(file_image.file)
            with image:
                image_extension = os.path.splitext(file_image.filename)[1]
                if image_extension.lower() not in [".jpeg", ".jpg"]:
                    raise HTTPException(status_code=400, detail="Please choose an image in JPEG/JPG format!")

                image_file_name = f"{str(uuid.uuid4())}.jpg"
                full_path = os.path.join(destination_folder, image_file_name)

                os.makedirs(destination_folder, exist_ok=True)
                image.save(full_path)

                image_path = os.path.join(destination_folder, image_file_name)

        post = Post(
            comment=post_create_schema.comment,
            path=image_path,
            category_id=post_create_schema.category_id,
            created_by=user.id,
            user_id=user.id,
            created_at=datetime.now(timezone.utc)
        )

        post_created = await repositories.post.create_post(post)
        post = await repositories.post.get_post_by_id(post_created.id)
        
        post_dto = PostSchema.from_orm(post)
        response = jsonable_encoder(
            ResponseModel(success=True, message="Registration completed successfully!", data=post_dto))
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)

    except HTTPException as ex:
        logger.error(f"HTTP error in UploadPost action: {ex.detail}")
        response = jsonable_encoder(ResponseModel(success=False, message=f"HTTP error: {ex.detail}"))
        return JSONResponse(status_code=ex.status_code, content=response)
    except Exception as ex:
        logger.error(f"Something went wrong inside UploadPost action: {ex}")
        response_model = jsonable_encoder(ResponseModel(success=False, message=f"Internal server error: {ex}"))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_model)
     
@router.delete("/post/{hashid}", name="Delete Post", status_code=status.HTTP_200_OK)
async def delete_post(
    hashid: str,
    repositories: RepositoryWrapper = Depends(get_repository_wrapper),
    current_user: AppUser = Depends(get_current_user)
):
    try:
        hashids = Hashids(salt=settings.SALT, min_length=settings.HASHLENGTH)  # Remplacez "your_salt" par le sel approprié
        decoded_ids = hashids.decode(hashid)
        if not decoded_ids:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        
        post_id = decoded_ids[0]
        post = await repositories.post.get_post_by_id(post_id)
        if not post:
            logger.error(f"Post with id: {post_id}, hasn't been found in db.")
            response_model = jsonable_encoder(ResponseModel(success=False, message="Not found"))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=response_model)

        if current_user.id != post.created_by:
            logger.error(f"This user is not the owner of the post.")
            response_model = jsonable_encoder(
                ResponseModel(success=False, message="This user is not the owner of the music!"))
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=response_model)

        post.is_active = False
        post.is_deleted = True

        await repositories.post.update_post(post)
        await repositories.save()

        response_model = jsonable_encoder(ResponseModel(success=True, message="Post deleted successfully!"))
        return JSONResponse(status_code=status.HTTP_200_OK, content=response_model)

    except Exception as ex:
        logger.error(f"Something went wrong inside Delete Post action: {ex}")
        response_model = jsonable_encoder(ResponseModel(success=False, message="Internal server error"))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response_model)
    
@router.put("/post/{hashid}", name="Update Post", status_code=status.HTTP_200_OK)
async def update_post(
    hashid: str,
    comment: Optional[str] = Form(None, alias='comment'),
    category_id: int = Form(..., alias='categoryId'),
    file_image: UploadFile = File(None, alias='fileImage'),
    repositories: RepositoryWrapper = Depends(get_repository_wrapper),
    current_user: AppUser = Depends(get_current_user)
):
    try:
        post_update_schema = PostUpdateSchema(
            comment=comment or "",
            category_id=category_id,
            file_image=file_image
        )
        if not post_update_schema:
            logger.error("Post object sent from client is null.")
            response = jsonable_encoder(ResponseModel(success=False, message="Post object is null"))
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response)

        hashids = Hashids(settings.SALT, settings.HASHLENGTH)
        decoded_ids = hashids.decode(hashid)
        if not decoded_ids:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

        post_id = decoded_ids[0]
        post = await repositories.post.get_post_by_id(post_id)
        if not post:
            logger.error(f"Post with id: {post_id}, hasn't been found in db.")
            response_model = jsonable_encoder(ResponseModel(success=False, message="Not found"))
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=response_model)

        if current_user.id != post.user_id:
            logger.error(f"This user is not the owner of the post.")
            response_model = jsonable_encoder(
                ResponseModel(success=False, message="This user is not the owner of the music!"))
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=response_model)

        post.updated_by = current_user.id
        post.comment = post_update_schema.comment
        post.category_id = post_update_schema.category_id

        await repositories.post.update_post(post)

        response = jsonable_encoder(ResponseModel(success=True, message="Post edited successfully!"))
        return JSONResponse(status_code=status.HTTP_200_OK, content=response)

    except Exception as ex:
        logger.error(f"Something went wrong inside Update Post action: {ex}")
        response = jsonable_encoder(ResponseModel(success=False, message=str(ex)))
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response)
