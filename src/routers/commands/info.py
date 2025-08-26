import aiofiles
from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name=__name__)


@router.message(Command("info"))
async def handle_info(message: Message) -> None:
    if isinstance(message, Message):
        async with aiofiles.open("src/texts/info_text.txt", encoding="utf-8") as file:
            await message.answer(text=await file.read(), parse_mode=ParseMode.HTML)
