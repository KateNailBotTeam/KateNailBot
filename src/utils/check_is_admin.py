from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models import User


async def check_is_admin(telegram_id: int, session: AsyncSession) -> bool:
    if telegram_id in settings.ADMIN_IDS:
        return True

    stmt = select(User.is_admin).where(User.telegram_id == telegram_id)
    result = await session.execute(stmt)

    is_admin = result.scalar_one_or_none()

    return bool(is_admin)
