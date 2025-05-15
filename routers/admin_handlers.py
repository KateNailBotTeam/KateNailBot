from aiogram import Router, types, F
from aiogram.filters import Command
from config import settings

router = Router(name=__name__)


@router.message(Command("admin", prefix='!/'), F.from_user.id.in_(settings.admin_ids))
async def admin_panel(message: types.Message):
    kb = [
        [types.InlineKeyboardButton(text="Управление расписанием", callback_data="change_schedule")],
        [types.InlineKeyboardButton(text="Управление записями", callback_data="change_bookings")],
    ]

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await message.answer(text="Выберите функцию", reply_markup=keyboard)



