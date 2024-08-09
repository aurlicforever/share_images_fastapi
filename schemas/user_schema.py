from __future__ import annotations
from datetime import datetime
from typing import Optional, List
from fastapi import Form
from pydantic import EmailStr, Field, ValidationError
from schemas.country_schema import CountrySchema
from schemas.base_model import BaseModel

class UserSchema(BaseModel):
    id: int
    name: Optional[str]
    user_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    photo: Optional[str]
    phone_number: Optional[str]
    is_confirmed: bool
    code_confirmation: Optional[str]
    code_confirmation_date: Optional[datetime]
    user_url: Optional[str]
    folder: Optional[str]
    country_id: Optional[int]
    country: Optional[CountrySchema] = None

    class Config:
        orm_mode = True

class UserCreateParameters(BaseModel):
    name: str
    email: EmailStr
    user_name: str = Field(..., alias="userName")
    password: str
    country_id: int = Field(..., alias="countryId")

class UserCreateSchema(BaseModel):
    name: str
    email: EmailStr
    user_name: str
    hashed_password: str
    country_id: int
    folder: str
    photo: str
    code_confirmation: str
    code_confirmation_date: datetime

    class Config:
        orm_mode = True

class UserUpdateSchema(BaseModel):
    name: str = Field(..., alias="name")
    user_name: str = Field(..., alias="userName")
    country_id: int = Field(..., alias="countryId")
    
    @classmethod
    def as_form(
        cls,
        name: str = Form(..., alias="name"),
        user_name: str = Form(..., alias="userName"),
        country_id: int = Form(..., alias="countryId")
    ) -> "UserUpdateSchema":
        return cls(
            name=name,
            user_name=user_name,
            country_id=country_id
        )
    

    # @validator("name", "user_name", "country_id", "country_code", "is_artist")
    # def not_empty(cls, value):
    #     if not value or not value.strip():
    #         raise ValueError("must not be empty")
    #     return value

def validate_user_update(user_update_schema: UserUpdateSchema) -> List[str]:
    errors = []
    try:
        user_update_schema.validate()
    except ValidationError as e:
        errors = [error["msg"] for error in e.errors()]
    return errors

class UserParameters(BaseModel):
    search_term: Optional[str] = None
    order_by: Optional[str] = 'id desc'
    page_number: int = 1
    page_size: int = 10

from schemas.country_schema import CountrySchema
UserSchema.update_forward_refs()