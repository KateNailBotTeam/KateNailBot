from aiogram.types import BotCommand

commands = [
    BotCommand(command="/start", description="Начать"),
    BotCommand(command="/book", description="Бронирование"),
    BotCommand(command="/info", description="Информация"),
    BotCommand(command="/admin", description="Для администратора"),
]
