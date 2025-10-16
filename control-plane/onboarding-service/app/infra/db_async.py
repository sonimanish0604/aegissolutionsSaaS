# app/infra/db_async.py
import os
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

_ENGINE = None
_SESSION_FACTORY = None

def _get_db_url() -> str:
    url = os.getenv("ASYNC_DATABASE_URL", "").strip()
    # expected format e.g. postgresql+asyncpg://user:pass@host:5432/dbname
    if not url:
        raise RuntimeError("ASYNC_DATABASE_URL is not set")
    return url

def _ensure_engine():
    global _ENGINE, _SESSION_FACTORY
    if _ENGINE is None:
        url = _get_db_url()
        _ENGINE = create_async_engine(url, future=True, pool_pre_ping=True)
        _SESSION_FACTORY = sessionmaker(bind=_ENGINE, class_=AsyncSession, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    _ensure_engine()
    async with _SESSION_FACTORY() as session:
        yield session