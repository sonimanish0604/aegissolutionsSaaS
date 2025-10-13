# app/infra/db_async.py
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

ASYNC_DATABASE_URL = os.getenv("DATABASE_URL_ASYNC")
SYNC_DATABASE_URL  = os.getenv("DATABASE_URL", "postgresql+psycopg2://aegis:aegis@localhost:5432/controlplane")

if not ASYNC_DATABASE_URL:
    # derive async URL from the sync one for local dev
    ASYNC_DATABASE_URL = SYNC_DATABASE_URL.replace("postgresql+psycopg2", "postgresql+asyncpg").replace(
        "postgresql://", "postgresql+asyncpg://"
    )

engine = create_async_engine(ASYNC_DATABASE_URL, future=True, pool_pre_ping=True)

SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session