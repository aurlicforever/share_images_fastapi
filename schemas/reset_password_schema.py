from pydantic import EmailStr
from schemas.base_model import BaseModel

class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str

class ChangePasswordSchema(BaseModel):
    email: EmailStr
    old_password: str
    new_password: str