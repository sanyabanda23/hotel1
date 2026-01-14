from datetime import date, datetime
from typing import Dict
from loguru import logger
from sqlalchemy import select, update, delete, func, or_, 
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from app.dao.base import BaseDAO
from app.dao.models import User, Room, Booking, Pay


class UserDAO(BaseDAO[User]):
    model = User


class RoomDAO(BaseDAO[Room]):
    model = Room


class PayDAO(BaseDAO[Pay]):
    model = Pay


class BookingDAO(BaseDAO[Booking]):
    model = Booking

    async def check_available_bookings(self, room_id: int, booking_date_start: date, booking_date_end: date):
        """Проверяет наличие существующих броней для комнаты на указанную дату."""
        try:
            if booking_date_start >= booking_date_end:
                raise ValueError("Дата начала должна быть раньше даты окончания")

            overlap_condition = and_(
                self.model.room_id == room_id,
                self.model.date_start < booking_date_end,      # A.start < B.end
                self.model.date_end > booking_date_start       # A.end > B.start
            )

            query = select(self.model).filter(overlap_condition)
            result = await self._session.execute(query)

           # Проверяем наличие хотя бы одной пересекающейся брони
           # Используем first() вместо all() для оптимизации
           return not result.scalars().first()

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при проверке доступности брони: {e}")
            raise
        except ValueError as e:
            logger.error(f"Некорректные входные данные: {e}")
            raise


    
    async def get_bookings_with_details(self, room_id: int):
        """
        Получает список всех бронирований комнаты с полной информацией о пользователе и общей суммы платежей.

        :param room_id: ID комнаты, брони которой нужно получить.
        :return: Список объектов Booking с загруженными данными о пользователе и общей суммы платежей.
        """
        try:
            query = (
                select(
                    self.model,
                    func.sum(self.model.pays.summ).label("total_payment")
                )
                    .join(self.model.user)           # JOIN для пользователя
                    .outerjoin(self.model.pays)     # LEFT JOIN для платежей
                    .filter(self.model.room_id == room_id)
                    .group_by(self.model.id)         # Группировка по ID бронирования
                )

            result = await self._session.execute(query)

            bookings = []
            for booking, total_payment in result.all():
                booking.total_payment = int(total_payment) if total_payment is not None else 0  # Если нет платежей → 0
                bookings.append(booking)
        
            return bookings
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении бронирований с деталями: {e}")
            return []

    async def complete_past_bookings(self):
        """
        Обновляет статус бронирований на 'completed', если дата и время бронирования уже прошли.
        """
        try:
            # Получаем текущее время
            now = datetime.now()
            subquery = select(TimeSlot.start_time).where(TimeSlot.id == self.model.time_slot_id).scalar_subquery()
            query = select(Booking.id).where(
                Booking.date < now.date(),
                self.model.status == "booked"
            ).union_all(
                select(Booking.id).where(
                    self.model.date == now.date(),
                    subquery < now.time(),
                    self.model.status == "booked"
                )
            )

            # Выполняем запрос и получаем id бронирований, которые нужно обновить
            result = await self._session.execute(query)
            booking_ids_to_update = result.scalars().all()

            if booking_ids_to_update:
                # Формируем запрос на обновление статуса бронирований
                update_query = update(Booking).where(
                    Booking.id.in_(booking_ids_to_update)
                ).values(status="completed")

                # Выполняем запрос на обновление
                await self._session.execute(update_query)

                # Подтверждаем изменения
                await self._session.commit()

                logger.info(f"Обновлен статус для {len(booking_ids_to_update)} бронирований на 'completed'")
            else:
                logger.info("Нет бронирований для обновления статуса.")

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении статуса бронирований: {e}")
            await self._session.rollback()

    # отмена имеющейся брони
    async def cancel_book(self, book_id: int):
        try:
            query = (
                update(self.model)
                .filter_by(id=book_id)
                .values(status="canceled")
                .execution_options(synchronize_session="fetch") # Указывает, как синхронизировать состояние сессии после обновления: "fetch" — перезагружает изменённые строки из БД
            )
            result = await self._session.execute(query)
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при отмене книги с ID {book_id}: {e}")
            await self._session.rollback()
            raise
    
    # удаление ммеющейся брони
    async def delete_book(self, book_id: int):
        try:
            query = delete(self.model).filter_by(id=book_id)
            result = await self._session.execute(query)
            logger.info(f"Удалено {result.rowcount} записей.")
            await self._session.flush()
            return result.rowcount
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении записей: {e}")
            raise

    async def book_count(self) -> Dict[str, int]: