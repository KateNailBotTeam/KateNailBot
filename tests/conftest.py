import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@pytest.fixture
def bot_mock():
    bot = AsyncMock(spec=Bot)
    bot.send_message = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.answer_callback_query = AsyncMock()
    bot.delete_message = AsyncMock()
    return bot


@pytest.fixture
def dispatcher(bot_mock):
    return Dispatcher(storage=MemoryStorage(), bot=bot_mock)
