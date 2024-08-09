from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Type, TypeVar, Generic
from pydantic import BaseModel
from sqlalchemy.sql import Select

T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db

    async def find_all(self) -> Select:
        return select(self.model)

    async def find_by_condition(self, condition) -> Select:
        return select(self.model).filter(condition)
        
    async def create(self, entity: T) -> T:
        async with self.db as session:
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity

    async def update(self, entity: T) -> T:
        async with self.db as session:
            await session.commit()
            await session.refresh(entity)
            return entity

    async def delete(self, entity: T):
        async with self.db as session:
            await session.delete(entity)
            await session.commit()

