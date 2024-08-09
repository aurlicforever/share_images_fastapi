from typing import Optional
from schemas.base_model import BaseModel

class CountrySchema(BaseModel):
    id: int
    phone: Optional[int]
    code: Optional[str]
    name: Optional[str]
    continent: Optional[str]
    continent_code: Optional[str]

    class Config:
        orm_mode = True
