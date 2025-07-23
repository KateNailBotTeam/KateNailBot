from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseService(Generic[ModelType]):
    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    async def get(self, session: AsyncSession, **filters: Any) -> ModelType | None:
        stmt = select(self.model).filter_by(**filters)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, session: AsyncSession, **filters: Any) -> list[ModelType]:
        stmt = select(self.model).filter_by(**filters)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, session: AsyncSession, obj: ModelType) -> ModelType:
        session.add(obj)
        await session.flush()
        await session.refresh(obj)
        return obj

    async def update(
        self, session: AsyncSession, obj_id: int, new_data: dict
    ) -> ModelType | None:
        obj = await self.get(session=session, id=obj_id)
        if not obj:
            return None
        for k, v in new_data.items():
            setattr(obj, k, v)

        await session.flush()
        await session.refresh(obj)
        return obj

    async def delete(self, session: AsyncSession, obj_id: int) -> bool:
        obj = await self.get(session=session, id=obj_id)
        if not obj:
            return False
        await session.delete(obj)
        await session.flush()
        return True
