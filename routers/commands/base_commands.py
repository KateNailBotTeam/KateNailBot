from aiogram import Router, types, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.utils import markdown
from static import commands
router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(message: types.Message):
    await message.bot.set_my_commands(commands=commands)

    inline_kb = [
        [types.InlineKeyboardButton(text="📅 Записаться", callback_data="book")],
        [types.InlineKeyboardButton(text="📝 Мои записи", callback_data="my_bookings")],
        [types.InlineKeyboardButton(text="📆 Расписание", callback_data="schedule")],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=inline_kb)
    await message.answer("Выберите действие:", reply_markup=keyboard)


@router.message(Command("info"))
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

@router.message(F.text.lower() == "id")
async def show_user_id(message: types.Message):
    await message.answer(text=f"Ваш user_id: {message.from_user.id}")