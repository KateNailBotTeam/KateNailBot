import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, TelegramObject

from src.exceptions.booking import BookingError
from src.exceptions.registration import RegistrationError
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

        except (InvalidCallbackError, InvalidMessageError) as e:
            logger.warning("Validation error: %s", str(e))
            await self._respond_and_cleanup(
                event, data, f"⚠️ Ошибка запроса: {e.message}"
            )

        except (InvalidUserError, RegistrationError) as e:
            logger.warning("User error: %s", str(e))
            await self._respond_and_cleanup(
                event, data, f"⚠️ Ошибка пользователя: {e.message}"
            )

        except BookingError as e:
            logger.exception("Booking error")  # TRY400 fixed
            await self._respond_and_cleanup(
                event, data, f"⚠️ Ошибка бронирования: {e.message}"
            )

        except (InvalidBotError, TokenNotFoundError) as e:
            logger.critical("Bot critical error: %s", str(e))
            await self._respond_and_cleanup(
                event, data, "⚠️ Произошла внутренняя ошибка бота"
            )

        except Exception:
            logger.exception("Unexpected error")  # TRY401 fixed
            await self._respond_and_cleanup(
                event, data, "⚠️ Произошла непредвиденная ошибка"
            )

        return None

    @staticmethod
    async def _respond_and_cleanup(
        event: TelegramObject, data: dict[str, Any], message: str
    ) -> None:
        """Отправляет сообщение об ошибке и очищает состояние"""
        try:
            if isinstance(event, CallbackQuery):
                await event.answer(message, show_alert=True)
                if isinstance(event.message, Message):
                    await event.message.edit_reply_markup(reply_markup=None)
            elif isinstance(event, Message):
                await event.answer(message)

            state: FSMContext | None = data.get("state")
            if state is None:
                logger.debug("Нет FSMContext в data — очистка состояния пропущена")
            elif not isinstance(state, FSMContext):
                logger.warning(
                    "В data['state'] содержится объект не типа FSMContext: %s",
                    type(state),
                )
            else:
                await state.clear()
                logger.debug("Состояние успешно очищено после ошибки")

        except Exception:
            logger.exception("Ошибка при отправке сообщения пользователю")
