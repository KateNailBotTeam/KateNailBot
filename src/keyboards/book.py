from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_book_main_menu() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="Записаться", callback_data="book")],
        [InlineKeyboardButton(text="Просмотреть мои записи", callback_data="my_book")],
        [InlineKeyboardButton(text="Отменить запись", callback_data="cancel_book")],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=kb)

    return keyboard
