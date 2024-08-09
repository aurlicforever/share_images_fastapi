from pydantic import Field, validator
from typing import Optional
from schemas.base_model import BaseModel

class QueryStringParameters(BaseModel):
    page_number: int = Field(default=1, alias='pageNumber')
    page_size: int = Field(default=10, alias='pageSize')
    search_term: Optional[str] = Field(None, alias='searchTerm')
    order_by: Optional[str] = Field(None)

    class Config:
        max_page_size = 50

    @validator('page_size', pre=True, always=True)
    def validate_page_size(cls, v):
        if v > cls.Config.max_page_size:
            return cls.Config.max_page_size
        return v
