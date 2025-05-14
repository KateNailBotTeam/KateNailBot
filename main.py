import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def handle_start(message: types.Message):
    await message.bot.send_message(
        chat_id=message.chat.id,
        text=f"Привет {message.from_user.full_name}! Меня зовут Катя и здесь ты сможешь записаться ко мне на маникюр",
        reply_to_message_id=message.message_id
    )

@dp.message(Command("help"))
async def handle_help(message: types.Message):
    help_text = """
    ✨ *Добро пожаловать в салон маникюра «Kate Nail»!* ✨

    📌 *Основные команды:*
    /start — Начать работу с ботом
    /help — Получить справку
    /book — Записаться онлайн
    /cancel — Отменить запись
    /price — Узнать цены
    /contacts — Контакты салона

    💅 *Услуги:*
    • Классический маникюр
    • Аппаратный маникюр
    • Покрытие гель-лаком
    • Дизайн ногтей
    • Укрепление ногтей
    • Педикюр

    ⏰ *Часы работы:*
    Пн-Пт: 10:00–20:00
    Сб-Вс: 11:00–19:00

    📍 *Адрес:*
    г. Москва, ул. Красивых Ногтей, 15 (м. «Маникюрная»)

    📞 *Телефон:* +7 (XXX) XXX-XX-XX

    ❗ *Правила:*
    - Отмена записи возможна не позднее чем за 3 часа до приёма.
    - Оплата наличными или картой.
    - При опоздании более чем на 15 минут время приёма сокращается.

    Для записи нажмите /book или выберите дату в меню ↓
    """
    await message.answer(text=help_text)


@dp.message()
async def echo_message(message: types.Message):
    await message.copy_to(chat_id=message.chat.id)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
