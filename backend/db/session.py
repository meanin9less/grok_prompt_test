import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.settings import settings

logger = logging.getLogger(__name__)

engine = None
SessionLocal: async_sessionmaker | None = None


def init_engine():
    global engine, SessionLocal
    if not settings.database_url:
        logger.warning("DATABASE_URL not set; DB connections will be unavailable")
        return
    # convert sync URL to async if needed
    url = settings.database_url
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(url, echo=False, future=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    logger.info("SQLAlchemy async engine initialized")


async def close_engine():
    global engine
    if engine:
        await engine.dispose()
        engine = None


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    if not SessionLocal:
        raise RuntimeError("DB engine not initialized; set DATABASE_URL")
    session = SessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
