import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

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

        except RegistrationError as e:
            logger.warning("Registration error: %s", str(e))
            await self._respond_and_cleanup(
                event, data, f"⚠️ Ошибка регистрации: {e}", clear_state=False
            )

        except (InvalidMessageError, InvalidCallbackError) as e:
            logger.warning("Validation error: %s", str(e))
            await self._respond_and_cleanup(event, data, f"⚠️ Ошибка запроса: {e}")

        except InvalidUserError as e:
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
        event: TelegramObject,
        data: dict[str, Any],
        message: str,
        clear_state: bool = True,
    ) -> None:
        """Отправка уведомления и очистка состояния (по умолчанию)"""
        try:
            await ErrorHandlerMiddleware._send_message(event, data, message)
            await ErrorHandlerMiddleware._remove_keyboard(event)
            if clear_state:
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
            elif isinstance(event, Message):
                await event.answer(message)
            elif isinstance(event, Update):
                # Извлекаем пользователя из Update
                user_id = None
                if event.message and event.message.from_user:
                    user_id = event.message.from_user.id
                elif event.callback_query and event.callback_query.from_user:
                    user_id = event.callback_query.from_user.id

                if user_id and bot:
                    await bot.send_message(chat_id=user_id, text=message)
                    logger.debug("Fallback сообщение отправлено через bot.send_message")
            else:
                logger.warning("Неизвестный тип события: %s", type(event))
        except Exception as e:
            logger.warning("Не удалось отправить сообщение пользователю: %s", e)

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
