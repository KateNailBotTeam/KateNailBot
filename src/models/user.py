from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.schedule import Schedule


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str | None] = mapped_column(String(50), nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(12), nullable=True, unique=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="user"
    )

    def __repr__(self) -> str:
        return (
            f"<User id={self.id} telegram_id={self.telegram_id}"
            f" first_name={self.first_name}>"
        )
