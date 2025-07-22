import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InaccessibleMessage,
    Message,
    ReplyKeyboardRemove,
)

router = Router(name=__name__)

logger = logging.getLogger(__name__)


@router.message(Command("cancel"))
@router.callback_query(F.data == "cancel")
async def cancel_handler(event: Message | CallbackQuery, state: FSMContext) -> None:
    logger.info("Cancel handler triggered by event: %s", type(event).__name__)
    response = "✅ Все действия отменены. Вы в главном меню"
    await state.clear()
    if isinstance(event, CallbackQuery):
        if event.message is None:
            logger.warning("CallbackQuery has no message attached.")
            await event.answer(response)
            return
        if isinstance(event.message, InaccessibleMessage):
            logger.warning("CallbackQuery message is InaccessibleMessage.")
            try:
                await event.answer(response)
                await event.message.answer(
                    text=response, reply_markup=ReplyKeyboardRemove()
                )
            except Exception as e:
                logger.error(
                    "Failed to handle inaccessible message: %s", e, exc_info=True
                )
            return
        try:
            await event.message.edit_text(text=response, reply_markup=None)
        except TelegramBadRequest:
            logger.warning(
                "TelegramBadRequest on edit_text, trying to send new message."
            )
            try:
                await event.message.answer(
                    text=response, reply_markup=ReplyKeyboardRemove()
                )
            except Exception as e:
                logger.error("Failed to send new message: %s", e, exc_info=True)
        except Exception as e:
            logger.error("Unexpected error: %s", e, exc_info=True)
        finally:
            await event.answer()
    else:
        try:
            await event.answer(text=response, reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            logger.error("Failed to answer message: %s", e, exc_info=True)
