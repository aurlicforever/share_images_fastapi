from schemas.base_model import BaseModel

class TokenModel(BaseModel):
    token: str
    refresh_token: str