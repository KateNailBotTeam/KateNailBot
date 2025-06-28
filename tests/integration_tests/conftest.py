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
async def clean_all_tables(session: AsyncSession):
    tables = Base.metadata.tables.keys()
    for table_name in tables:
        print(table_name)
        await session.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
    await session.commit()
