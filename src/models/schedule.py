from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base

if TYPE_CHECKING:
    from src.models.user import User


class VisitDurationTimeEnum(Enum):
    QUARTER_HOUR = 15
    HALF_HOUR = 30
    HOUR = 60
    TWO_HOURS = 120
    THREE_HOURS = 180
    FOUR_HOURS = 240


class Schedule(Base):
    __tablename__ = "schedules"

    visit_datetime: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, unique=True
    )
    visit_duration: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=VisitDurationTimeEnum.HALF_HOUR.value,
        server_default=text(str(VisitDurationTimeEnum.HALF_HOUR.value)),
    )
    is_booked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    user_telegram_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.telegram_id", onupdate="CASCADE", ondelete="CASCADE"),
        nullable=True,
        default=None,
        server_default=text("NULL"),
    )

    is_approved: Mapped[bool] = mapped_column(
        Boolean, nullable=True, default=None, server_default=text("NULL")
    )

    user: Mapped["User"] = relationship("User", back_populates="schedules")
