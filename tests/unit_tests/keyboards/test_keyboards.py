import pytest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.keyboards.book import create_book_main_menu_kb


@pytest.mark.asyncio
async def test_book_keyboard() -> None:
    keyboard = create_book_main_menu_kb()
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 4

    expected_buttons = [
        "Записаться",
        "Просмотреть мои записи",
        "Отменить запись",
        "ВЫХОД",
    ]

    for i, expected_text in enumerate(expected_buttons):
        button = keyboard.inline_keyboard[i][0]
        assert isinstance(button, InlineKeyboardButton)
        assert button.text == expected_text
