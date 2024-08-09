from pydantic import BaseModel, EmailStr

class ConfirmEmailSchema(BaseModel):
    email: EmailStr
    code: str