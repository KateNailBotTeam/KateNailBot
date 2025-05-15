import asyncio
import logging

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def handle_start(message: types.Message):
    inline_kb = [
        [types.InlineKeyboardButton(text="📅 Записаться", callback_data="book")],
        [types.InlineKeyboardButton(text="📝 Мои записи", callback_data="my_bookings")],
        [types.InlineKeyboardButton(text="📆 Расписание", callback_data="schedule")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=inline_kb)
    await message.answer("Выберите действие:", reply_markup=keyboard)


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


@dp.callback_query(F.data == "book")
async def book(callback: types.CallbackQuery):
    await callback.message.answer(text="Тут будет логика бронирования")


@dp.callback_query(F.data == "my_bookings")
async def my_bookings(callback: types.CallbackQuery):
    await callback.message.answer(text="Мои бронирования : ...")


@dp.callback_query(F.data == "show_schedule")
async def show_schedule(callback: types.CallbackQuery):
    await callback.message.answer(
        text="Тут должен быть календарь с расписанием сеансов"
    )


async def main():
    logging.basicConfig(level=logging.DEBUG)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
