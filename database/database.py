from collections.abc import AsyncGenerator, Callable

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import settings


def get_engine() -> AsyncEngine:
    engine = create_async_engine(
        url=settings.db_url, echo=True, pool_size=50, max_overflow=10
    )
    return engine


def get_session_factory(
    engine: AsyncEngine | None = None,
) -> Callable[[], AsyncSession]:
    if engine is None:
        engine = get_engine()
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


def get_session_dependency(
    engine: AsyncEngine | None = None,
) -> Callable[[], AsyncGenerator[AsyncSession, None]]:
    session_factory = get_session_factory(engine)

    async def _get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    return _get_session
