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


@router.message(Command("cancel"))
@router.callback_query(F.data == "cancel")
async def cancel_handler(event: Message | CallbackQuery, state: FSMContext) -> None:
    response = "✅ Все действия отменены. Вы в главном меню"

    await state.clear()

    if isinstance(event, CallbackQuery):
        if event.message is None:
            await event.answer(response)
            return

        if isinstance(event.message, InaccessibleMessage):
            try:
                await event.answer(response)
                await event.message.answer(
                    text=response, reply_markup=ReplyKeyboardRemove()
                )
            except Exception as e:
                print(f"Failed to handle inaccessible message: {e}")
            return

        try:
            await event.message.edit_text(text=response, reply_markup=None)
        except TelegramBadRequest:
            try:
                await event.message.answer(
                    text=response, reply_markup=ReplyKeyboardRemove()
                )
            except Exception as e:
                print(f"Failed to send new message: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            await event.answer()
    else:
        try:
            await event.answer(text=response, reply_markup=ReplyKeyboardRemove())
        except Exception as e:
            print(f"Failed to answer message: {e}")
