from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from repositories.repository_wrapper import RepositoryWrapper
from database.database import get_db

async def get_repository_wrapper(db: AsyncSession = Depends(get_db)) -> RepositoryWrapper:
    return RepositoryWrapper(db)