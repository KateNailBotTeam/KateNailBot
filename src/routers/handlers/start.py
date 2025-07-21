from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.registration import (
    InvalidFirstNameError,
    InvalidPhoneFormatError,
    InvalidTelegramIdError,
    PhoneAlreadyExistsError,
)
from src.keyboards.start import ask_about_phone_kb
from src.services.user import UserService
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
        await callback.message.edit_text(text="Введите номер в формате +7XXXXXXXXXX:")


@router.callback_query(F.data == "profile_skip_phone")
async def skip_phone(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user_service: UserService,
) -> None:
    if isinstance(callback.message, Message):
        await callback.answer()
        await state.update_data(phone=None)
        data = await state.get_data()
        await finish_registration(callback.message, data, state, session, user_service)


@router.message(RegistrationState.waiting_for_phone)
async def save_phone(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user_service: UserService,
) -> None:
    await state.update_data(phone=message.text)
    data = await state.get_data()
    try:
        await finish_registration(message, data, state, session, user_service)
    except PhoneAlreadyExistsError:
        await message.answer(
            "Этот номер телефона уже зарегистрирован. Пожалуйста, введите другой номер:"
        )
    except InvalidPhoneFormatError:
        await message.answer(
            "Этот номер телефона не соответствует формату."
            " Пожалуйста, введите другой номер:"
        )


async def finish_registration(
    message: Message,
    data: dict,
    state: FSMContext,
    session: AsyncSession,
    user_service: UserService,
) -> None:
    telegram_id = data.get("telegram_id")
    first_name = data.get("first_name")
    phone = data.get("phone")

    if not isinstance(telegram_id, int):
        raise InvalidTelegramIdError()

    if not isinstance(first_name, str) or not first_name:
        raise InvalidFirstNameError()

    user = await user_service.create_or_get_user(
        session=session,
        telegram_id=telegram_id,
        first_name=first_name,
    )

    user = await user_service.update_name(
        session=session,
        user=user,
        new_name=first_name,
    )

    if phone:
        user = await user_service.update_number(
            session=session, user=user, new_number=phone
        )

    await message.answer(
        f"Вы зарегистрированы!\nИмя: {user.first_name}\n"
        f"Телефон: {user.phone or 'не указан'}"
    )

    # Очистка состояния FSM
    await state.clear()
