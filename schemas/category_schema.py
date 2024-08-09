from typing import Optional
from schemas.base_model import BaseModel

class CategorySchema(BaseModel):
    id: int
    name: Optional[str] = None

    class Config:
        orm_mode = True