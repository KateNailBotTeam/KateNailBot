from aiogram import F, Router
from aiogram.types import CallbackQuery

router = Router(name=__name__)


@router.callback_query(F.data == "profile_keep_name")
async def keep_name(callback: CallbackQuery) -> None:
    pass


@router.callback_query(F.data == "profile_change_name")
async def change_name(callback: CallbackQuery) -> None:
    pass
