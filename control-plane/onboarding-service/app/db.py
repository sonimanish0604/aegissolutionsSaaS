# app/db.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import os

ASYNC_DATABASE_URL = os.getenv("DATABASE_URL_ASYNC")
engine = create_async_engine(ASYNC_DATABASE_URL, pool_pre_ping=True, future=True)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session