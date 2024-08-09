from __future__ import annotations
from fastapi import Form
from pydantic import Field
from typing import Optional
from schemas.category_schema import CategorySchema
from datetime import datetime
from typing import Optional
from schemas.query_string_parameters import QueryStringParameters
from schemas.country_schema import CountrySchema
from schemas.base_model import BaseModel

class PostSchema(BaseModel):
    id: int
    comment: Optional[str]
    path: Optional[str]
    size: Optional[str]
    is_published: bool
    user_id: Optional[int]
    user: Optional[UserSchema] = None
    category_id: Optional[int]
    category: Optional[CategorySchema] = None
    created_at: Optional[datetime]

    class Config:
        orm_mode = True

class PostCreateSchema(BaseModel):
    comment: Optional[str] = Form(None, alias="comment")
    category_id: int = Form(..., alias="categoryId")
    
    @classmethod
    def as_form(
        cls,
        comment: Optional[str] = Form(None, alias="comment"),
        category_id: int = Form(..., alias="categoryId"),
    ) -> "PostCreateSchema":
        return cls(
            comment=comment,
            category_id=category_id,
            # file_image=file_image
        )

class PostUpdateSchema(BaseModel):
    comment: Optional[str] = Field(None, alias="comment")
    category_id: int = Field(..., alias="categoryId")


class PostParameters(QueryStringParameters):
    order_by: str = "id"
    search_term: Optional[str] = Field(None, alias="searchTerm")


class PostWithActionsCountSchema(BaseModel):
    post: PostSchema
    likes_count: int
    comments_count: int
    current_user_like: bool
    
from schemas.user_schema import UserSchema

# Update forward references
PostSchema.update_forward_refs()
PostWithActionsCountSchema.update_forward_refs()
UserSchema.update_forward_refs()
CountrySchema.update_forward_refs()