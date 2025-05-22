from unittest.mock import AsyncMock

import pytest

from src.keyboards.book import create_book_main_menu
from src.routers.commands.base import book


@pytest.mark.asyncio
async def test_command_book() -> None:
    message = AsyncMock()
    await book(message)
    message.answer.assert_called_with(
        text="Управление записями", reply_markup=create_book_main_menu()
    )
