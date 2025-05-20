from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards.book import create_book_main_menu
from keyboards.start import create_start_keyboard
from texts.info_text import info_text

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    await message.answer("Выберите действие:", reply_markup=create_start_keyboard())


@router.message(Command("info"))
async def handle_help(message: Message) -> None:
    await message.answer(text=info_text, parse_mode=ParseMode.HTML)


@router.message(Command("book"))
async def book(message: Message) -> None:
    await message.answer(
        text="Управление записями", reply_markup=create_book_main_menu()
    )
