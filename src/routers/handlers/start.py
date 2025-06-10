from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.keyboards.start import ask_about_phone_kb
from src.states.registration import RegistrationState

router = Router(name=__name__)


@router.callback_query(F.data == "profile_keep_name")
async def keep_name(callback: CallbackQuery) -> None:
    if isinstance(callback.message, Message):
        await callback.answer()
        await callback.message.edit_text(
            text="Хотите добавить номер телефона?", reply_markup=ask_about_phone_kb()
        )


@router.callback_query(F.data == "profile_change_name")
async def change_name(callback: CallbackQuery, state: FSMContext) -> None:
    if isinstance(callback.message, Message):
        await state.set_state(RegistrationState.waiting_for_name)
        await callback.answer()
        await callback.message.edit_text("Введите новое имя:")


@router.message(RegistrationState.waiting_for_name)
async def set_new_name(message: Message, state: FSMContext) -> None:
    await state.update_data(first_name=message.text)
    await message.answer(
        text="Хотите добавить номер телефона?", reply_markup=ask_about_phone_kb()
    )


@router.callback_query(F.data == "profile_add_phone")
async def add_phone(callback: CallbackQuery, state: FSMContext) -> None:
    if isinstance(callback.message, Message):
        await state.set_state(RegistrationState.waiting_for_phone)
        await callback.answer()
        await callback.message.edit_text(text="Введите номер:")


@router.callback_query(F.data == "profile_skip_phone")
async def skip_phone(callback: CallbackQuery, state: FSMContext) -> None:
    if isinstance(callback.message, Message):
        await callback.answer()
        data = await state.get_data()
        await finish_registration(callback.message, data, state)


@router.message(RegistrationState.waiting_for_phone)
async def save_phone(message: Message, state: FSMContext) -> None:
    await state.update_data(phone=message.text)
    data = await state.get_data()
    await finish_registration(message, data, state)


async def finish_registration(message: Message, data: dict, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        f"Вы зарегистрированы!\nИмя: {data.get('first_name')}\n"
        f"Телефон: {data.get('phone', 'не указан')}"
    )
