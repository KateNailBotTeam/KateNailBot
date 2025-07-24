from datetime import time

from sqlalchemy import Integer, Time, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class ScheduleSettings(Base):
    __tablename__ = "schedule_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    working_days: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), nullable=False, default=[0, 1, 2, 3, 4]
    )
    start_working_time: Mapped[time] = mapped_column(
        Time, nullable=False, default=time(9, 0), server_default=text("'09:00:00'")
    )
    end_working_time: Mapped[time] = mapped_column(
        Time, nullable=False, default=time(18, 0), server_default=text("'18:00:00'")
    )
    booking_days_ahead: Mapped[int] = mapped_column(
        Integer, nullable=False, default=14, server_default=text("14")
    )
    slot_duration_minutes: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30, server_default=text("30")
    )
