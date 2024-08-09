from pydantic import Field
from typing import Optional
from datetime import datetime
from schemas.user_schema import UserSchema
from schemas.query_string_parameters import QueryStringParameters
from schemas.base_model import BaseModel

class CommentSchema(BaseModel):
    id: int
    comment_text: Optional[str] = None
    comment_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    user_id: int
    post_id: int
    user: Optional[UserSchema] = None

    class Config:
        orm_mode = True

class CommentCreateSchema(BaseModel):
    post_id: int = Field(..., alias="postId")
    comment_text: str = Field(..., alias="commentText")
    user: Optional[UserSchema] = None

    class Config:
        orm_mode = True

class CommentParameters(QueryStringParameters):
    order_by: str = "created_at desc"