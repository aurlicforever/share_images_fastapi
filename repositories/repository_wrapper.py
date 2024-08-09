# repository_wrapper.py
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.user_repository import UserRepository
from repositories.post_repository import PostRepository
from repositories.category_repository import CategoryRepository
from repositories.country_repository import CountryRepository
from repositories.like_post_repository import LikePostRepository
from repositories.comment_repository import CommentRepository

class RepositoryWrapper:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._user_repository = None
        self._post_repository = None
        self._category_repository = None
        self._country_repository = None
        self._like_post_repository = None
        self._comment_repository = None

    @property
    def user(self) -> UserRepository:
        if self._user_repository is None:
            self._user_repository = UserRepository(self.db)
        return self._user_repository

    @property
    def post(self) -> PostRepository:
        if self._post_repository is None:
            self._post_repository = PostRepository(self.db)
        return self._post_repository

    @property
    def category(self) -> CategoryRepository:
        if self._category_repository is None:
            self._category_repository = CategoryRepository(self.db)
        return self._category_repository

    @property
    def country(self) -> CountryRepository:
        if self._country_repository is None:
            self._country_repository = CountryRepository(self.db)
        return self._country_repository

    @property
    def like_post(self) -> LikePostRepository:
        if self._like_post_repository is None:
            self._like_post_repository = LikePostRepository(self.db)
        return self._like_post_repository

    @property
    def comment(self) -> CommentRepository:
        if self._comment_repository is None:
            self._comment_repository = CommentRepository(self.db)
        return self._comment_repository

    async def save(self):
        await self.db.commit()
