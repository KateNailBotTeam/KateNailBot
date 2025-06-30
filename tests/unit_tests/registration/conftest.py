from unittest.mock import AsyncMock

import pytest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message


@pytest.fixture
def message_mock():
    mock = AsyncMock(spec=Message)
    mock.answer = AsyncMock()
    mock.edit_text = AsyncMock()
    return mock


@pytest.fixture
def callback_mock(message_mock):
    mock = AsyncMock(spec=CallbackQuery)
    mock.message = message_mock
    mock.answer = AsyncMock()
    return mock


@pytest.fixture
def state_mock():
    mock = AsyncMock(spec=FSMContext)
    mock.set_state = AsyncMock()
    return mock
