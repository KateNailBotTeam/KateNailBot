from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any

from aiogram.types import CallbackQuery, Message

from src.exceptions.telegram_object import InvalidCallbackError


def validate_callback(need_data: bool = False, need_message: bool = False) -> Callable:
    """
    Декоратор для валидации callback-запросов

    :param need_data: Проверять ли callback.data
    :param need_message: Проверять ли callback.message
    """

    def decorator(func: Callable[..., Coroutine[Any, Any, None]]) -> Callable:
        @wraps(func)
        async def wrapper(callback: CallbackQuery, *args: Any, **kwargs: Any) -> None:
            if need_message and not isinstance(callback.message, Message):
                raise InvalidCallbackError(
                    "callback.message должен быть объектом Message"
                )

            if need_data and not isinstance(callback.data, str):
                raise InvalidCallbackError("callback.data должен быть строкой")
            return await func(callback, *args, **kwargs)

        return wrapper

    return decorator
