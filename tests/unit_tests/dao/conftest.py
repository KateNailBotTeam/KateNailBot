import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import engine, session_factory
from src.models.base import Base

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))


@pytest_asyncio.fixture()
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
