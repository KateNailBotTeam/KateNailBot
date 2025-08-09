# ruff: noqa: ARG001
import asyncio
from datetime import date

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import engine, session_factory
from src.models.base import Base
from src.models.schedule_settings import ScheduleSettings
from src.models.user import User
from src.services.schedule import ScheduleService
from src.services.user import UserService


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
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


@pytest.fixture
async def user_service():
    service = UserService()
    return service


@pytest.fixture
async def schedule_service():
    service = ScheduleService()
    return service


@pytest.fixture
async def schedule_settings(session: AsyncSession) -> ScheduleSettings:
    settings = ScheduleSettings()
    session.add(settings)
    await session.commit()
    return settings


@pytest.fixture
async def create_users(session: AsyncSession, users_quantity=5):
    users = []
    for i in range(users_quantity):
        user = User(
            telegram_id=i * 10000 + 1,
            username=f"user_{i}"[:50],
            first_name=f"TestUser{i}"[:100],
            phone=f"+7{9000000000 + i}",
            is_admin=False,
        )
        users.append(user)
    session.add_all(users)
    await session.commit()
    return users


@pytest.fixture
async def available_dates(
    session: AsyncSession,
    schedule_service: ScheduleService,
    schedule_settings: ScheduleSettings,
) -> list[date]:
    dates = await schedule_service.get_available_dates(
        session=session, schedule_settings=schedule_settings
    )
    return sorted(dates)


@pytest.fixture
def time_slots(
    schedule_service: ScheduleService,
    available_dates: list[date],
    schedule_settings: ScheduleSettings,
):
    visit_date = available_dates[0]
    return schedule_service.get_time_slots(
        visit_date=visit_date, schedule_settings=schedule_settings
    )
