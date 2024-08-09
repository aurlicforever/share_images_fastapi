from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.base_repository import BaseRepository
from core.sort_helper import SortHelper
from schemas.country_schema import CountrySchema
from models.country import Country

class CountryRepository(BaseRepository[Country]):
    
    def __init__(self, db: AsyncSession):
        super().__init__(Country, db)

    async def get_countries(self) -> List[CountrySchema]:
        sort_helper = SortHelper()
        condition = (Country.is_active == True)
        country_query = await self.find_by_condition(condition)
        sorted_country_query = sort_helper.apply_sort(country_query, "name")
        
        result = await self.db.execute(sorted_country_query)
        result = result.scalars().all()
        country_schemas = [CountrySchema.from_orm(country) for country in result]

        return country_schemas
