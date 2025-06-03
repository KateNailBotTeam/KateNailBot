from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from src.config import settings
from src.keyboards.admin import create_admin_keyboard

router = Router(name=__name__)


@router.message(Command("admin", prefix="!/"), F.from_user.id.in_(settings.ADMIN_IDS))
async def admin_panel(message: Message) -> None:
    await message.answer(text="Выберите функцию", reply_markup=create_admin_keyboard())
