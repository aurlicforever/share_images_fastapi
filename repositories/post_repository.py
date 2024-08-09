from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
from sqlalchemy.sql import func
from sqlalchemy import and_
from models.post import Post
from schemas.post_schema import PostParameters, PostSchema
from schemas.page_list_schema import PagedList
from repositories.base_repository import BaseRepository
from core.sort_helper import SortHelper
from models.app_user import AppUser

class PostRepository(BaseRepository[Post]):
    def __init__(self, db: AsyncSession):
        super().__init__(Post, db)

    async def get_all_posts(self, post_parameters: PostParameters) -> PagedList[PostSchema]:
        sort_helper = SortHelper()
        posts_query = await self.find_by_condition(and_(Post.is_active == True))
        posts_query = self._search_by_comment(posts_query, post_parameters.search_term)
        if post_parameters.search_term is None:
            sorted_posts_query = sort_helper.apply_sort(posts_query, "id desc")
        else:
            sorted_posts_query = sort_helper.apply_sort(posts_query, post_parameters.order_by)
        
        total_count_result = await self.db.execute(select(func.count()).select_from(sorted_posts_query.subquery()))
        total_count = total_count_result.scalar_one()
        result = await self.db.execute(
            sorted_posts_query.offset((post_parameters.page_number - 1) * post_parameters.page_size)
            .limit(post_parameters.page_size)
            .options(selectinload(Post.user).selectinload(AppUser.country), selectinload(Post.category))
        )

        paginated_posts = result.scalars().all()
        
        return PagedList[PostSchema].to_paged_list(paginated_posts, total_count, post_parameters.page_number, post_parameters.page_size)

    def _search_by_comment(self, posts_query, search_term: Optional[str]):
        if not search_term:
            return posts_query
        posts_query = posts_query.filter(Post.comment.ilike(f"%{search_term}%"))
        return posts_query

    async def get_post_by_id(self, post_id: int) -> Post:
        condition = and_(Post.id == post_id, Post.is_active == True)
        query = await self.find_by_condition(condition)
        result = await self.db.execute(query.options(selectinload(Post.user).selectinload(AppUser.country), selectinload(Post.category)))
        post = result.scalar_one_or_none()
        return post
    
    async def get_post_by_category(self, category_id: int, post_parameters: PostParameters) -> Post:
        sort_helper = SortHelper()
        posts_query = await self.find_by_condition(and_(Post.category_id == category_id, Post.is_active == True))
        posts_query = self._search_by_comment(posts_query, post_parameters.search_term)
        if post_parameters.search_term is None:
            sorted_posts_query = sort_helper.apply_sort(posts_query, "id desc")
        else:
            sorted_posts_query = sort_helper.apply_sort(posts_query, post_parameters.order_by)
        
        total_count_result = await self.db.execute(select(func.count()).select_from(sorted_posts_query.subquery()))
        total_count = total_count_result.scalar_one()
        result = await self.db.execute(
            sorted_posts_query.offset((post_parameters.page_number - 1) * post_parameters.page_size)
            .limit(post_parameters.page_size)
            .options(selectinload(Post.user).selectinload(AppUser.country), selectinload(Post.category))
        )
        paginated_posts = result.scalars().all()
        
        return PagedList[PostSchema].to_paged_list(paginated_posts, total_count, post_parameters.page_number, post_parameters.page_size)

    async def get_user_posts(self, user_id: int, post_parameters: PostParameters) -> PagedList[PostSchema]:
        sort_helper = SortHelper()
        posts_query = await self.find_by_condition(and_(Post.user_id == user_id, Post.is_active == True))
        sorted_posts_query = sort_helper.apply_sort(posts_query, "id desc")
        total_count_result = await self.db.execute(select(func.count()).select_from(sorted_posts_query.subquery()))
        total_count = total_count_result.scalar_one()

        result = await self.db.execute(
            sorted_posts_query.offset((post_parameters.page_number - 1) * post_parameters.page_size)
            .limit(post_parameters.page_size)
            .options(selectinload(Post.user).selectinload(AppUser.country), selectinload(Post.category))
        )

        paginated_posts = result.scalars().all()
        return PagedList[PostSchema].to_paged_list(paginated_posts, total_count, post_parameters.page_number, post_parameters.page_size)

    async def update_post(self, post: Post):
        await self.update(post)

    async def create_post(self, post: Post):
        return await self.create(post)

