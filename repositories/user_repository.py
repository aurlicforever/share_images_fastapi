from fastapi import Depends
from sqlalchemy import func, or_, select, text, and_
from sqlalchemy.orm import Query
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.base_repository import BaseRepository
from models.app_user import AppUser
from schemas.page_list_schema import PagedList
from core.sort_helper import SortHelper
from schemas.user_schema import UserSchema, UserParameters
from sqlalchemy.orm import selectinload

class UserRepository(BaseRepository[AppUser]):
    
    def __init__(self, db: AsyncSession):
        super().__init__(AppUser, db)

    async def get_users(self, user_parameters: UserParameters) -> PagedList[UserSchema]:
        sort_helper = SortHelper()
        condition = and_(AppUser.is_active == True)
        query = await self.find_by_condition(condition)
        query = self._search(query, user_parameters.search_term)
        
        sorted_query = sort_helper.apply_sort(query, user_parameters.order_by or "id desc")
        
        total_count_result = await self.db.execute(select(func.count()).select_from(sorted_query.subquery()))
        total_count = total_count_result.scalar_one()
        result = await self.db.execute(
            sorted_query
            .offset((user_parameters.page_number - 1) * user_parameters.page_size)
            .limit(user_parameters.page_size)
            .options(selectinload(AppUser.country))
        )
        
        paginated_users = result.scalars().all()
        user_schemas = [UserSchema.from_orm(user) for user in paginated_users]

        return PagedList[UserSchema].to_paged_list(user_schemas, total_count, user_parameters.page_number, user_parameters.page_size)


    def _search(self, query: Query, search_term: str) -> Query:
        if not search_term:
            return query
        search = f"%{search_term.strip().lower()}%"
        return query.filter(
            (AppUser.user_name.ilike(search)) |
            (AppUser.name.ilike(search)) |
            (AppUser.email.ilike(search))
        )

    async def get_user_by_id(self, user_id: int) -> AppUser:
        condition = and_(AppUser.is_active == True, AppUser.id == user_id)
        users_query = await self.find_by_condition(condition)
        result = await self.db.execute(users_query.options(selectinload(AppUser.country)))
        user = result.scalar_one_or_none()
        return user
    
    async def get_user_by_user_name(self, user_name: int) -> AppUser:
        condition = and_(AppUser.is_active == True, AppUser.user_name == user_name)
        users_query = await self.find_by_condition(condition)
        result = await self.db.execute(users_query.options(selectinload(AppUser.country)))
        user = result.scalar_one_or_none()
        return user
    
    async def get_user_by_email(self, email: str) -> AppUser:
        condition = and_(AppUser.is_active == True, AppUser.email == email)
        users_query = await self.find_by_condition(condition)
        result = await self.db.execute(users_query.options(selectinload(AppUser.country)))
        user = result.scalar_one_or_none()
        return user
    
    async def get_user_active_or_not(self, login: str) -> AppUser:
        condition = or_(AppUser.user_name == login, AppUser.email == login)
        users_query = await self.find_by_condition(condition)
        result = await self.db.execute(users_query.options(selectinload(AppUser.country)))
        user = result.scalar_one_or_none()
        return user
    
    async def create_user(self, user: AppUser):
        user_created = await self.create(user)
        return user_created
    
    async def update_user(self, user: AppUser):
        await self.update(user)
    