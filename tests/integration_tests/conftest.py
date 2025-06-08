# ruff: noqa: ARG001
import asyncio
import os

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import engine, session_factory
from src.models.base import Base

os.environ["MODE"] = "TEST"


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def session(prepare_database) -> AsyncSession:
    async with session_factory() as session:
        yield session


@pytest.fixture(autouse=True)
async def clean_users_table(session: AsyncSession):
    await session.execute(text("DELETE FROM users"))
    await session.commit()
