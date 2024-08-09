from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from sqlalchemy.orm import selectinload
from models.comment import Comment
from models.app_user import AppUser
from schemas.comment_schema import CommentParameters, CommentSchema
from schemas.page_list_schema import PagedList
from repositories.base_repository import BaseRepository
from core.sort_helper import SortHelper

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db: AsyncSession):
        super().__init__(Comment, db)

    async def count_comments(self, post_id: int) -> int:
        result = await self.db.execute(
            select(func.count()).where(Comment.post_id == post_id, Comment.is_active == True)
        )
        return result.scalar_one()

    async def create_comment(self, comment: Comment):
        return await self.create(comment)

    async def delete_comment(self, comment: Comment):
        await self.delete(comment)

    async def get_comment_by_id(self, comment_id: int) -> Comment:
        condition = and_(Comment.id == comment_id, Comment.is_active == True)
        query = await self.find_by_condition(condition)
        result = await self.db.execute(query.options(selectinload(Comment.user).selectinload(AppUser.country)))
        return result.scalar_one_or_none()

    async def get_post_comments(self, post_id: int, comment_parameters: CommentParameters) -> PagedList[CommentSchema]:
        sort_helper= SortHelper()
        condition = and_(Comment.post_id == post_id, Comment.is_active == True)
        query = await self.find_by_condition(condition)
        sorted_query = sort_helper.apply_sort(query, comment_parameters.order_by or "id desc")
        
        total_count_result = await self.db.execute(select(func.count()).select_from(sorted_query.subquery()))
        total_count = total_count_result.scalar_one()

        result = await self.db.execute(
            query.offset((comment_parameters.page_number - 1) * comment_parameters.page_size)
            .limit(comment_parameters.page_size)
            .options(selectinload(Comment.user).selectinload(AppUser.country))
        )
        paginated_comments = result.scalars().all()
        comments_schemas = [CommentSchema.from_orm(comment) for comment in paginated_comments]
        return PagedList[CommentSchema].to_paged_list(comments_schemas, total_count, comment_parameters.page_number, comment_parameters.page_size)

    async def update_comment(self, comment: Comment):
        await self.update(comment)
