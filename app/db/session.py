from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base

engine = create_async_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession
)


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


__all__ = ["engine", "SessionLocal", "Base", "get_db"]
