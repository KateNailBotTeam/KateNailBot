import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, TelegramObject

from src.exceptions import RegistrationError
from src.exceptions.booking import BookingError
from src.exceptions.telegram_object import (
    InvalidBotError,
    InvalidCallbackError,
    InvalidMessageError,
    InvalidUserError,
)
from src.exceptions.token import TokenNotFoundError

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except (InvalidMessageError, InvalidCallbackError) as e:
            logger.warning("Validation error: %s", str(e))
            await self._respond_and_cleanup(event, data, f"⚠️ Ошибка запроса: {e}")
        except (InvalidUserError, RegistrationError) as e:
            logger.warning("User error: %s", str(e))
            await self._respond_and_cleanup(event, data, f"⚠️ Ошибка пользователя: {e}")
        except BookingError as e:
            logger.exception("Booking error")
            await self._respond_and_cleanup(event, data, f"⚠️ Ошибка бронирования: {e}")
        except (InvalidBotError, TokenNotFoundError) as e:
            logger.critical("Bot critical error: %s", str(e))
            await self._respond_and_cleanup(
                event, data, "⚠️ Произошла внутренняя ошибка бота"
            )
        except Exception:
            logger.exception("Unexpected error")
            await self._respond_and_cleanup(
                event, data, "⚠️ Произошла непредвиденная ошибка"
            )
        return None

    @staticmethod
    async def _respond_and_cleanup(
        event: TelegramObject, data: dict[str, Any], message: str
    ) -> None:
        """Основная функция — вызывает отдельные шаги"""
        try:
            await ErrorHandlerMiddleware._send_message(event, data, message)
            await ErrorHandlerMiddleware._remove_keyboard(event)
            await ErrorHandlerMiddleware._clear_state(data)
        except Exception:
            logger.exception("Ошибка при уведомлении пользователя и очистке состояния")

    @staticmethod
    async def _send_message(
        event: TelegramObject, data: dict[str, Any], message: str
    ) -> None:
        bot = data.get("bot")
        try:
            if isinstance(event, CallbackQuery):
                await event.answer(message, show_alert=True)
                logger.debug("Alert отправлен пользователю через CallbackQuery")
            elif isinstance(event, Message):
                await event.answer(message)
                logger.debug("Сообщение отправлено пользователю через Message.answer")
            else:
                logger.warning(
                    "Неизвестный тип события: %s. Отправляю fallback", type(event)
                )
                if bot and hasattr(event, "from_user") and event.from_user:
                    await bot.send_message(chat_id=event.from_user.id, text=message)
        except Exception as e:
            logger.warning("Не удалось отправить сообщение пользователю: %s", e)
            if bot and hasattr(event, "from_user") and event.from_user:
                await bot.send_message(chat_id=event.from_user.id, text=message)
                logger.debug("Fallback сообщение отправлено через bot.send_message")

    @staticmethod
    async def _remove_keyboard(event: TelegramObject) -> None:
        if isinstance(event, CallbackQuery) and isinstance(event.message, Message):
            try:
                await event.message.edit_reply_markup(reply_markup=None)
                logger.debug("Клавиатура удалена")
            except Exception as e:
                logger.warning("Не удалось убрать клавиатуру: %s", e)

    @staticmethod
    async def _clear_state(data: dict[str, Any]) -> None:
        state = data.get("state")
        if state and isinstance(state, FSMContext):
            await state.clear()
            logger.debug("FSMContext очищен после ошибки")
        elif state:
            logger.warning("state присутствует, но не типа FSMContext: %s", type(state))
        else:
            logger.debug("FSMContext в data отсутствует — очистка пропущена")
