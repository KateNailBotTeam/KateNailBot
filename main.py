import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.utils import markdown
from aiogram.enums import ParseMode

from config import settings

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def handle_start(message: types.Message):
    text = markdown.text(
        f"Привет {markdown.hbold(message.from_user.full_name)}! Здесь делают хороший маникюр. Открой меню для записи.",
        sep='\n'
        )
    await message.answer(text=text, reply_to_message_id=message.message_id, parse_mode=ParseMode.HTML)


@dp.message(Command("help"))
async def handle_help(message: types.Message):
    help_text = markdown.text(
        markdown.hbold("✨ Добро пожаловать в салон маникюра «Kate Nail»! ✨\n\n"),
        markdown.hbold("📌 Основные команды:\n"),
        "/start — Начать работу с ботом\n",
        "/help — Получить справку\n",
        "/book — Записаться онлайн\n",
        "/cancel — Отменить запись\n",
        "/price — Узнать цены\n",
        "/contacts — Контакты салона\n\n",
        markdown.hbold("💅 Услуги:\n"),
        "• Классический маникюр\n",
        "• Аппаратный маникюр\n",
        "• Покрытие гель-лаком\n",
        "• Дизайн ногтей\n",
        "• Укрепление ногтей\n",
        "• Педикюр\n\n",
        markdown.hbold("⏰ Часы работы:\n"),
        "Пн–Пт: 10:00–20:00\n",
        "Сб–Вс: 11:00–19:00\n\n",
        markdown.hbold("📍 Адрес:\n"),
        "г. Москва, ул. Красивых Ногтей, 15 (м. «Маникюрная»)\n\n",
        "📞 Телефон: +7 (XXX) XXX-XX-XX\n\n",
        markdown.hbold("❗ Правила:\n"),
        "- Отмена записи возможна не позднее чем за 3 часа до приёма.\n",
        "- Оплата наличными или картой.\n",
        "- При опоздании более чем на 15 минут время приёма сокращается.\n\n",
        "Для записи нажмите /book или выберите дату в меню ↓",
    )
    await message.answer(text=help_text, parse_mode=ParseMode.HTML)


@dp.message()
async def echo_message(message: types.Message):
    await message.copy_to(chat_id=message.chat.id)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
