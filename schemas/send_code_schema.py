from pydantic import EmailStr
from schemas.base_model import BaseModel

class SendCodeSchema(BaseModel):
    email: EmailStr
    reason: str
