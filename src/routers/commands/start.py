from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils import markdown
from sqlalchemy.ext.asyncio import AsyncSession

from src.keyboards.start import ask_about_name_kb
from src.schemas.user import UserSchema
from src.services.user import UserService

router = Router(name=__name__)


@router.message(CommandStart())
async def handle_start(
    message: Message,
    session: AsyncSession,
    user_service: UserService,
    state: FSMContext,
) -> None:
    if not message.from_user:
        await message.answer("Не удалось получить информацию о пользователе.")
        return

    telegram_id = message.from_user.id

    user = await user_service.create_or_get_user(
        session=session,
        telegram_id=telegram_id,
        first_name=message.from_user.first_name,
    )
    user_schema_dict = UserSchema.model_validate(user).model_dump(mode="json")
    await state.update_data(
        telegram_id=telegram_id,
        first_name=user.first_name,
        user_schema_dict=user_schema_dict,
    )

    await message.answer(
        text=f"Как к вам обращаться?\nСейчас: {markdown.hbold(user.first_name)}",
        reply_markup=ask_about_name_kb(),
        parse_mode=ParseMode.HTML,
    )
