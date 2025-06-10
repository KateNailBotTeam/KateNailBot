from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils import markdown

from src.keyboards.start import ask_about_name_kb

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    if message.from_user:
        await state.set_data(
            {
                "first_name": message.from_user.first_name,
                "telegram_id": message.from_user.id,
            }
        )
        await message.answer(
            text=f"Как к вам обращаться?\nСейчас: "
            f"{markdown.hbold(message.from_user.first_name)}",
            reply_markup=ask_about_name_kb(),
            parse_mode=ParseMode.HTML,
        )
    else:
        await message.answer("Не удалось получить информацию о пользователе.")
