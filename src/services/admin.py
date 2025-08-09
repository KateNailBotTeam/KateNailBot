import asyncio
import logging
from datetime import date, datetime, timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy import and_, delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.attributes import flag_modified

from src.keyboards.calendar import WEEKDAYS
from src.models import User
from src.models.day_off import DaysOff
from src.models.schedule import Schedule
from src.models.schedule_settings import ScheduleSettings
from src.services.base import BaseService
from src.texts.status_appointments import APPOINTMENT_TYPE_STATUS

logger = logging.getLogger(__name__)


class AdminService(BaseService[Schedule]):
    def __init__(self) -> None:
        super().__init__(Schedule)

    @staticmethod
    async def get_booking(
        session: AsyncSession,
        booking_id: int,
    ) -> Schedule | None:
        logger.debug("Получение бронирования id=%d", booking_id)
        stmt = (
            select(Schedule)
            .options(joinedload(Schedule.user))
            .where(Schedule.id == booking_id)
        )
        result = await session.execute(stmt)
        booking = result.scalar_one_or_none()
        logger.info("Бронь: %s", booking_id)

        return booking

    @staticmethod
    async def get_all_bookings(
        session: AsyncSession,
    ) -> list[Schedule]:
        stmt = (
            select(Schedule)
            .options(joinedload(Schedule.user))
            .where(and_(Schedule.is_booked, Schedule.visit_datetime >= datetime.now()))
            .order_by(Schedule.visit_datetime)
        )
        result = await session.execute(stmt)
        bookings = list(result.scalars().all())

        logger.info("Получены все бронирования: %d", len(bookings))
        return bookings

    async def set_booking_approval(
        self, session: AsyncSession, schedule_id: int, approved: bool | None
    ) -> Schedule | None:
        updated_booking = await self.update(
            obj_id=schedule_id, session=session, new_data={"is_approved": approved}
        )
        status = APPOINTMENT_TYPE_STATUS.get(approved)
        logger.info(
            "Обновлено подтверждение записи id=%s на значение %s", schedule_id, status
        )
        return updated_booking

    @staticmethod
    async def set_workdays(
        first_day: date,
        last_day: date,
        is_work: bool,
        session: AsyncSession,
    ) -> None:
        if first_day > last_day:
            logger.warning(
                "Попытка установить дни с неправильным диапазоном:"
                " начальная дата позже конечной (%s > %s)",
                first_day,
                last_day,
            )
            raise ValueError("first_day_off не может быть позже last_day_off")

        try:
            if is_work:
                await session.execute(
                    delete(DaysOff).where(DaysOff.day_off.between(first_day, last_day))
                )
                await session.commit()

            else:
                current_date = first_day
                while current_date <= last_day:
                    await session.execute(
                        insert(DaysOff)
                        .values(day_off=current_date)
                        .on_conflict_do_nothing(index_elements=["day_off"])
                    )
                    current_date += timedelta(days=1)

                await session.commit()

            logger.info(
                "%s дни с %s по %s обновлены.",
                "Рабочие" if is_work else "Нерабочие",
                first_day,
                last_day,
            )

        except SQLAlchemyError as e:
            await session.rollback()
            logger.exception("Ошибка при обновлении дней: %s", exc_info=e)
            raise

    @staticmethod
    async def toggle_working_day(
        session: AsyncSession, day_index: int, schedule_settings: ScheduleSettings
    ) -> None:
        """Переключает день между рабочим и нерабочим, обновляет запись в БД."""

        if not 0 <= day_index <= len(WEEKDAYS):
            raise ValueError("day_index должен быть в диапазоне 0-6")

        if day_index in schedule_settings.working_days:
            schedule_settings.working_days.remove(day_index)
        else:
            schedule_settings.working_days.append(day_index)

        schedule_settings.working_days.sort()
        flag_modified(schedule_settings, "working_days")

        await session.commit()

    @staticmethod
    async def send_message_from_admin_to_all_users(
        bot: Bot,
        session: AsyncSession,
        text_message: str,
        disable_notification: bool = True,
    ) -> str:
        stmt = select(User.telegram_id).where(User.is_admin.is_(False))
        result = await session.execute(stmt)
        users_telegram_ids = result.scalars().all()

        tasks = []

        for user_telegram_id in users_telegram_ids:
            tasks.append(
                bot.send_message(
                    chat_id=user_telegram_id,
                    text=text_message,
                    disable_notification=disable_notification,
                )
            )

        results = await asyncio.gather(*tasks, return_exceptions=True)

        errors_details = ""
        successful_sendings = 0
        failed_sendings = 0

        for user_telegram_id, send_result in zip(
            users_telegram_ids, results, strict=False
        ):
            if isinstance(send_result, TelegramAPIError):
                logger.warning(
                    "Сообщение пользователю с telegram id %s не отправлено. Ошибка: %s",
                    user_telegram_id,
                    result,
                )
                errors_details += f"- telegram_id {user_telegram_id}: {result}\n"
                failed_sendings += 1

            elif isinstance(send_result, Exception):
                logger.warning(
                    "Произошла непредвиденная ошибка telegram id %s. Ошибка %s",
                    user_telegram_id,
                    result,
                )
                errors_details += f"- telegram_id {user_telegram_id}: {result}\n"
                failed_sendings += 1
            else:
                successful_sendings += 1

        logger.info(
            "Рассылка завершена. Успешно: %d, Ошибок: %d, Всего пользователей: %d",
            successful_sendings,
            failed_sendings,
            len(users_telegram_ids),
        )

        summary_text = (
            f"📢 Рассылка завершена.\n"
            f"👥 Всего пользователей: {len(users_telegram_ids)}\n"
            f"✅ Успешно отправлено сообщений: {successful_sendings}\n"
            f"❌ Не удалось отправить сообщения: {failed_sendings}\n"
        )

        if errors_details:
            summary_text += "\n⚠️ Ошибки по пользователям:\n" + errors_details

        return summary_text
