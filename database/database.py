from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.config import settings

engine = create_async_engine(
    url=settings.db_url, echo=True, pool_size=50, max_overflow=10
)

session_factory = async_sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session
