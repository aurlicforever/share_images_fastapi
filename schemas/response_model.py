from schemas.base_model import BaseModel
from typing import Optional, Any

class ResponseModel(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None