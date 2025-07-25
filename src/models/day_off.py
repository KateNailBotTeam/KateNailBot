from datetime import date

from sqlalchemy import Date
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class DaysOff(Base):
    __tablename__ = "days_off"

    day_off: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
