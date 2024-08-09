from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Type
from models.like_post import LikePost
from repositories.base_repository import BaseRepository
from schemas.query_string_parameters import QueryStringParameters
from sqlalchemy.orm import selectinload
from core.sort_helper import SortHelper
from schemas.page_list_schema import PagedList

class LikePostRepository(BaseRepository[LikePost]):
    def __init__(self, db: AsyncSession):
        super().__init__(LikePost, db)

    async def count_post_likes(self, post_id: int) -> int:
        stmt = await self.find_by_condition(LikePost.post_id == post_id)
        result = await self.db.execute(select(func.count()).select_from(stmt.subquery()))
        count_likes = result.scalar()
        return count_likes

    async def create_like(self, like_post: LikePost) -> LikePost:
        return await self.create(like_post)

    async def delete_like(self, like_post: LikePost):
        await self.delete(like_post)

    async def get_post_user_like(self, user_id: int, post_id: int) -> LikePost:
        stmt = await self.find_by_condition((LikePost.user_id == user_id) & (LikePost.post_id == post_id))
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def update_like(self, like_post: LikePost) -> LikePost:
        return await self.update(like_post)

    async def get_post_likes(self, post_id: int, query_string_parameters: QueryStringParameters, sort_helper: SortHelper) -> PagedList:
        condition = LikePost.post_id == post_id
        likes_query = await self.find_by_condition(condition)
        sorted_likes_query = sort_helper.apply_sort(likes_query, query_string_parameters.order_by or "id desc")
        
        total_count_result = await self.db.execute(select(func.count()).select_from(sorted_likes_query.subquery()))
        total_count = total_count_result.scalar_one()
        result = await self.db.execute(
            sorted_likes_query.offset((query_string_parameters.page_number - 1) * query_string_parameters.page_size)
            .limit(query_string_parameters.page_size)
            .options(selectinload(LikePost.user))
        )
        paginated_likes = result.scalars().all()
        
        return PagedList.to_paged_list(paginated_likes, total_count, query_string_parameters.page_number, query_string_parameters.page_size)
