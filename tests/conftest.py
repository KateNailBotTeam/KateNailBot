from unittest.mock import AsyncMock

import pytest
from aiogram import Bot, Dispatcher
from aiogram.types import Chat, Message, User


@pytest.fixture(scope="session")
async def bot() -> AsyncMock:
    return AsyncMock(spec=Bot)


@pytest.fixture(scope="session")
async def dispatcher() -> Dispatcher:
    return Dispatcher()
