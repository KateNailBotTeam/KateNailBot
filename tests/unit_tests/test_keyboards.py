import pytest
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from src.keyboards.book import create_book_main_menu


@pytest.mark.asyncio
async def test_book_keyboard() -> None:
    keyboard = create_book_main_menu()
    assert isinstance(keyboard, InlineKeyboardMarkup)
    assert len(keyboard.inline_keyboard) == 3

    expected_buttons = ["Записаться", "Просмотреть свои записи", "Отменить запись"]

    for i, expected_text in enumerate(expected_buttons):
        button = keyboard.inline_keyboard[i][0]
        assert isinstance(button, InlineKeyboardButton)
        assert button.text == expected_text
