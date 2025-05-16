from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def create_start_keyboard() -> InlineKeyboardMarkup:
    inline_kb = [
        [InlineKeyboardButton(text="📅 Записаться", callback_data="book")],
        [InlineKeyboardButton(text="📝 Мои записи", callback_data="my_bookings")],
        [InlineKeyboardButton(text="📆 Расписание", callback_data="schedule")],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_kb)

    return keyboard
