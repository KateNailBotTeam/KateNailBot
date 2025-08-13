from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, User
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.telegram_object import InvalidMessageError, InvalidUserError
from src.keyboards.admin import create_admin_keyboard
from src.utils.get_admins_ids import get_admin_ids

router = Router(name=__name__)


@router.message(Command("admin", prefix="!/"))
async def admin_panel(
    message: Message,
    session: AsyncSession,
) -> None:
    if not isinstance(message, Message):
        raise InvalidMessageError("message должен быть объектом Message")
    if not isinstance(message.from_user, User):
        raise InvalidUserError("ошибка типа телеграм User")

    if message.from_user.id not in await get_admin_ids(session):
        await message.answer(text="⛔ У вас нет доступа, так как вы не админ")
        return

    await message.answer(text="Выберите функцию", reply_markup=create_admin_keyboard())
