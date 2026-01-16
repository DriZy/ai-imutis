"""Database session and engine setup."""

from sqlalchemy import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import get_settings


def _build_async_url(raw_url: str) -> str:
    url = make_url(raw_url)
    if url.drivername in {"postgres", "postgresql"}:
        url = url.set(drivername="postgresql+asyncpg")
    return str(url)


_settings = get_settings()
ASYNC_DATABASE_URL = _build_async_url(_settings.database_url)
engine: AsyncEngine = create_async_engine(ASYNC_DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    """Provide an async DB session dependency."""

    async with SessionLocal() as session:
        yield session
