import logging
from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.exceptions.booking import BookingError
from src.models.schedule import Schedule
from src.models.schedule_settings import ScheduleSettings
from src.services.base import BaseService

logger = logging.getLogger(__name__)


class ScheduleService(BaseService[Schedule]):
    def __init__(self) -> None:
        super().__init__(Schedule)

    def is_working_day(
        self, visit_date: date, schedule_settings: ScheduleSettings
    ) -> bool:
        """Проверяет, является ли дата рабочим днём (пн-пт)"""
        return visit_date.weekday() in schedule_settings.working_days

    def get_available_dates(self, schedule_settings: ScheduleSettings) -> list[date]:
        """Возвращает список доступных дат для записи (14 рабочих дней вперёд)"""
        available_dates: list[date] = []
        current_date = datetime.now().date()

        while len(available_dates) < schedule_settings.booking_days_ahead:
            if self.is_working_day(
                visit_date=current_date, schedule_settings=schedule_settings
            ):
                available_dates.append(current_date)
            current_date += timedelta(days=1)

        logger.debug("Доступные даты: %s", available_dates)
        return available_dates

    @staticmethod
    def get_time_slots(
        visit_date: date, schedule_settings: ScheduleSettings
    ) -> list[time]:
        """Генерирует список временных слотов для указанной даты"""
        time_slots = []
        last_visit = datetime.combine(
            visit_date, schedule_settings.end_working_time
        ) - timedelta(minutes=schedule_settings.slot_duration_minutes)

        start_visit = datetime.combine(visit_date, schedule_settings.start_working_time)

        while start_visit <= last_visit:
            time_slots.append(start_visit.time())
            start_visit += timedelta(minutes=schedule_settings.slot_duration_minutes)

        logger.debug("Сгенерировано слотов: %d", len(time_slots))
        return time_slots

    async def is_slot_available(
        self,
        session: AsyncSession,
        visit_date: date,
        visit_time: time,
        schedule_settings: ScheduleSettings,
    ) -> bool:
        """Проверяет доступность слота для бронирования"""
        dt = datetime.combine(visit_date, visit_time)

        day_stmt = select(Schedule.is_day_off).where(
            Schedule.visit_datetime.between(
                datetime.combine(visit_date, time.min),
                datetime.combine(visit_date, time.max),
            )
        )
        result = await session.execute(day_stmt)
        is_day_off = result.scalar_one_or_none()
        if is_day_off:
            logger.warning("Дата %s является выходным", visit_date)
            raise BookingError("Выбранная дата является выходным днем")

        if visit_date not in self.get_available_dates(schedule_settings):
            logger.warning("Недоступная дата: %s", visit_date)
            raise BookingError("Выбранная дата недоступна для записи")

        if visit_time not in self.get_time_slots(
            visit_date=visit_date, schedule_settings=schedule_settings
        ):
            logger.warning("Недоступное время: %s", visit_time)
            raise BookingError("Выбранное время недоступно для записи")

        stmt = select(Schedule.is_booked).where(Schedule.visit_datetime == dt)
        result = await session.execute(stmt)
        booked = result.scalar_one_or_none()

        is_available = booked is None or not booked
        logger.debug("Слот %s доступен: %s", dt, is_available)
        return is_available

    @staticmethod
    async def get_booking_slots_for_date(
        session: AsyncSession,
        visit_date: date,
    ) -> list[datetime]:
        logger.info("Получение занятых слотов на дату: %s", visit_date)
        start_datetime = datetime.combine(visit_date, time.min)
        end_datetime = datetime.combine(visit_date, time.max)
        stmt = (
            select(Schedule.visit_datetime)
            .where(
                and_(
                    Schedule.visit_datetime.between(start_datetime, end_datetime),
                    Schedule.is_booked,
                )
            )
            .order_by(Schedule.visit_datetime)
        )
        result = await session.execute(stmt)
        slots = list(result.scalars().all())
        logger.info("Занятые слоты на дату %s: %s", visit_date, slots)
        return slots

    async def create_busy_slot(
        self,
        session: AsyncSession,
        visit_date: date,
        visit_time: time,
        user_telegram_id: int,
        schedule_settings: ScheduleSettings,
    ) -> Schedule:
        """Создаёт занятый слот в расписании"""
        visit_datetime = datetime.combine(visit_date, visit_time)

        if not await self.is_slot_available(
            session, visit_date, visit_time, schedule_settings
        ):
            logger.warning("Слот уже занят: %s %s", visit_date, visit_time)
            raise BookingError("Это время уже занято")

        new_slot = Schedule(
            visit_datetime=visit_datetime,
            visit_duration=schedule_settings.slot_duration_minutes,
            is_booked=True,
            user_telegram_id=user_telegram_id,
        )

        await self.add(session=session, obj=new_slot)
        logger.info(
            "Создан новый слот: %s для пользователя %d", new_slot, user_telegram_id
        )
        return new_slot

    @staticmethod
    async def show_user_schedules(
        session: AsyncSession, user_telegram_id: int
    ) -> list[datetime]:
        """Возвращает список будущих записей пользователя"""
        logger.debug("Получение записей для пользователя %d", user_telegram_id)
        stmt = (
            select(Schedule.visit_datetime)
            .where(
                and_(
                    Schedule.user_telegram_id == user_telegram_id,
                    Schedule.is_booked,
                    Schedule.visit_datetime > datetime.now(),
                )
            )
            .order_by(Schedule.visit_datetime)
        )

        result = await session.execute(stmt)
        schedules = list(result.scalars().all())

        logger.debug(
            "Найдено записей для user_id=%d: %d", user_telegram_id, len(schedules)
        )
        return schedules

    @staticmethod
    async def cancel_booking(
        session: AsyncSession, user_telegram_id: int, datetime_to_cancel: datetime
    ) -> None:
        """Отменяет указанную запись пользователя"""
        logger.debug(
            "Попытка отменить запись для пользователя %d на %s",
            user_telegram_id,
            datetime_to_cancel,
        )
        stmt = delete(Schedule).where(
            and_(
                Schedule.user_telegram_id == user_telegram_id,
                Schedule.visit_datetime == datetime_to_cancel,
            )
        )

        result = await session.execute(stmt)
        await session.commit()

        if not result.rowcount:
            logger.warning(
                "Запись не найдена: user_id=%d, datetime=%s",
                user_telegram_id,
                datetime_to_cancel,
            )
            raise BookingError("Запись не найдена")

        logger.info(
            "Запись отменена: user_id=%d, datetime=%s",
            user_telegram_id,
            datetime_to_cancel,
        )
