from math import ceil
from typing import Generic, List, TypeVar
from schemas.base_model import BaseModel

class MetaData(BaseModel):
    total_count: int
    page_size: int
    current_page: int
    total_pages: int

T = TypeVar("T")

class PagedList(BaseModel, Generic[T]):
    items: List[T]
    meta_data: MetaData

    @staticmethod
    def to_paged_list(items, total_count: int, page_number: int, page_size: int):
        total_pages = ceil(total_count / page_size)
        meta_data = MetaData(
            total_count=total_count,
            page_size=page_size,
            current_page=page_number,
            total_pages=total_pages
        )
        return PagedList(items=items, meta_data=meta_data)