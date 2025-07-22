from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.keyboards.book import create_book_main_menu_kb

router = Router(name=__name__)


@router.message(Command("book"))
async def book(message: Message) -> None:
    await message.answer(
        text="Управление записями", reply_markup=create_book_main_menu_kb()
    )
