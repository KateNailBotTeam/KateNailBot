from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.models import User


async def get_admin_ids(session: AsyncSession) -> set[int]:
    stmt = select(User.telegram_id).where(User.is_admin.is_(True))
    result = await session.execute(stmt)
    admin_id_from_db = result.scalars().all()

    admin_ids = set()
    admin_ids.update(settings.ADMIN_IDS)
    admin_ids.update(admin_id_from_db)

    return {admin_id for admin_id in admin_ids if admin_id}
