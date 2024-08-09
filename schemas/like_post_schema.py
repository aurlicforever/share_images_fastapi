from typing import Optional
from datetime import datetime
from schemas.user_schema import UserSchema
from schemas.post_schema import PostSchema
from schemas.base_model import BaseModel

class LikePostSchema(BaseModel):
    id: int
    user_id: int
    post_id: int
    is_liked: bool
    post: Optional[PostSchema] = None
    user: Optional[UserSchema] = None
    created_at: datetime

    class Config:
        orm_mode = True

class LikePostCreateSchema(BaseModel):
    post_id: str
    is_liked: bool