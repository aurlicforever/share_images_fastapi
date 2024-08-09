from typing import List
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.base_repository import BaseRepository
from core.sort_helper import SortHelper
from schemas.category_schema import CategorySchema
from models.category import Category
from sqlalchemy.orm import selectinload

class CategoryRepository(BaseRepository[Category]):
    
    def __init__(self, db: AsyncSession):
        super().__init__(Category, db)

    async def get_categories(self) -> List[CategorySchema]:
        sort_helper = SortHelper()
        condition = (Category.is_active == True)
        query = await self.find_by_condition(condition)
        sorted_query = sort_helper.apply_sort(query, "name")
        
        result = await self.db.execute(sorted_query)
        result = result.scalars().all()
        category_schemas = [CategorySchema.from_orm(category) for category in result]

        return category_schemas
    
    async def get_category_by_name(self, name: str) -> Category:
        condition = and_(Category.name == name, Category.is_active == True)
        query = await self.find_by_condition(condition)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()