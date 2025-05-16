from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from config import settings
from keyboards.admin import create_admin_keyboard

router = Router(name=__name__)


@router.message(Command("admin", prefix='!/'), F.from_user.id.in_(settings.admin_ids))
async def admin_panel(message: Message):
    await message.answer(text="Выберите функцию", reply_markup=create_admin_keyboard())
