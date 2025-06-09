from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

from src.texts.info_text import info_text

router = Router(name=__name__)


@router.message(Command("info"))
async def handle_info(message: Message) -> None:
    if isinstance(message, Message):
        await message.answer(text=info_text, parse_mode=ParseMode.HTML)
