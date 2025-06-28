from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base


class BaseDAO:
    def __init__(self, model: type[Base]) -> None:
        self.model = model

    async def get(self, session: AsyncSession, obj_id: int) -> object | None:
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, session: AsyncSession, obj: Base) -> object:
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return obj

    async def update(
        self, session: AsyncSession, obj_id: int, new_data: dict
    ) -> object | None:
        obj = await self.get(session=session, obj_id=obj_id)
        if not obj:
            return None
        for k, v in new_data.items():
            setattr(obj, k, v)

        await session.flush()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, obj_id: int) -> bool:
        obj = await self.get(session=session, obj_id=obj_id)
        if not obj:
            return False
        await session.delete(obj)
        await session.flush()
        return True
