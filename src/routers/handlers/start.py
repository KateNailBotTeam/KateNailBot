from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions import RegistrationError
from src.keyboards.start import ask_about_phone_kb
from src.models import User
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
        await finish_registration(callback, data, state, session, user_service)


@router.message(RegistrationState.waiting_for_phone)
async def save_phone(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user_service: UserService,
) -> None:
    try:
        await state.update_data(phone=message.text)
        data = await state.get_data()
        await finish_registration(message, data, state, session, user_service)
    except RegistrationError as e:
        print(e)


async def finish_registration(
    obj: CallbackQuery | Message,
    data: dict,
    state: FSMContext,
    session: AsyncSession,
    user_service: UserService,
) -> None:
    telegram_id = data.get("telegram_id")
    first_name = data.get("first_name")
    phone = data.get("phone")
    user_schema_dict = data.get("user_schema_dict")

    if not isinstance(telegram_id, int):
        raise RegistrationError("Ошибка в telegram id")

    if not isinstance(first_name, str) or not first_name:
        raise RegistrationError("Ошибка в first_name пользователя")

    if not isinstance(user_schema_dict, dict):
        raise RegistrationError("Ошибка в получении пользователя из данных состояния")

    user = User(**user_schema_dict)

    data = {}

    if user.first_name != first_name:
        data["first_name"] = first_name

    if phone and user.phone != phone:
        data["phone"] = phone

    updated_user = await user_service.update(
        session=session, obj_id=user.id, new_data=data
    )

    if not updated_user:
        raise RegistrationError("Невозможно обновить несуществующего пользователя")

    text = (
        f"Вы зарегистрированы!\nИмя: {updated_user.first_name}\n"
        f"Телефон: {updated_user.phone or 'не указан'}"
    )

    if isinstance(obj, CallbackQuery) and isinstance(obj.message, Message):
        await obj.message.edit_text(text=text, reply_markup=None)
        await obj.answer()
    elif isinstance(obj, Message):
        await obj.answer(text)

    # Очистка состояния FSM
    await state.clear()
