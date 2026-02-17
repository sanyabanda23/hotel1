from datetime import date, datetime, timezone
from typing import Dict
from loguru import logger
from sqlalchemy import select, update, delete, func, and_, extract 
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
        except ValueError as e:
            logger.error(f"Некорректные входные данные: {e}")


    async def get_bookings_with_details_date_start(self):
        """
        Получает список всех бронирований комнаты с полной информацией о пользователе и общей суммы платежей.
        Где дата заезда равна текущему дню
        :return: Список объектов Booking с загруженными данными о пользователе и общей суммы платежей.
        """
        now = datetime.now(timezone.utc)
        try:
            query = (
                select(
                    self.model,
                    func.sum(Pay.summ).label("total_payment")
                )
                    .join(self.model.user)           # JOIN для пользователя
                    .join(self.model.room)
                    .outerjoin(self.model.pays)     # LEFT JOIN для платежей
                    .filter(self.model.date_start == now.date())
                    .group_by(self.model.id)         # Группировка по ID бронирования
                )

            result = await self._session.execute(query)
            rows = result.all()
            
            if rows:
                bookings = []
                for booking, total_payment in rows:
                    total = int(total_payment) if total_payment is not None else 0  # Если нет платежей → 0
                    bookings.append((booking, total))
                
                logger.info(f"Сегодня заселяется {len(bookings)} гостей")
                return bookings
            else:
                logger.info(f"Сегодня заселений не будет")
                return []
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении бронирований с деталями: {e}")
            return []
    
    async def get_bookings_with_details_date_end(self):
        """
        Получает список всех бронирований комнаты с полной информацией о пользователе и общей суммы платежей.
        Где дата выезда равна текущему дню
        :return: Список объектов Booking с загруженными данными о пользователе и общей суммы платежей.
        """
        now = datetime.now(timezone.utc)
        try:
            query = (
                select(
                    self.model,
                    func.sum(Pay.summ).label("total_payment")
                )
                    .join(self.model.user)           # JOIN для пользователя
                    .join(self.model.room)
                    .outerjoin(self.model.pays)     # LEFT JOIN для платежей
                    .filter(self.model.date_end == now.date())
                    .group_by(self.model.id)         # Группировка по ID бронирования
                )

            result = await self._session.execute(query)
            rows = result.all()
            
            if rows:
                bookings = []
                for booking, total_payment in rows:
                    total = int(total_payment) if total_payment is not None else 0  # Если нет платежей → 0
                    bookings.append((booking, total))
                
                logger.info(f"Сегодня выезжает {len(bookings)} гостей")
                return bookings
            else:
                logger.info(f"Сегодня заселений не будет")
                return []
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении бронирований с деталями: {e}")
            return []
        
    async def get_bookings_with_details_year(self, room_id: int, year: int):
        """
        Получает список всех бронирований комнаты с полной информацией о пользователе и общей суммы платежей.
        За указаный год
        :param room_id: ID комнаты, брони которой нужно получить.
        :return: Список объектов Booking с загруженными данными о пользователе и общей суммы платежей.
        """
        try:
            query = (
                select(
                    self.model,
                    func.sum(Pay.summ).label("total_payment")
                )
                    .join(self.model.user)           # JOIN для пользователя
                    .join(self.model.room)
                    .outerjoin(self.model.pays)     # LEFT JOIN для платежей
                    .filter(self.model.room_id == room_id, extract('year', self.model.date_start) == year)
                    .group_by(self.model.id)         # Группировка по ID бронирования
                )

            result = await self._session.execute(query)
            rows = result.all()
            
            if rows:
                bookings = []
                for booking, total_payment in rows:
                    total = int(total_payment) if total_payment is not None else 0  # Если нет платежей → 0
                    bookings.append((booking, total))
                
                logger.info(f"Для комнаты №{room_id} найдено {len(bookings)} в {year} году.")
                return bookings
            else:
                logger.info(f"Для комнаты №{room_id} нет бронирований в {year} году.")
                return []
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении бронирований с деталями: {e}")
            return []

    async def get_bookings_with_details(self, room_id: int):
        """
        Получает список всех бронирований комнаты с полной информацией о пользователе и общей суммы платежей.
        За текущий период со дня запроса
        :param room_id: ID комнаты, брони которой нужно получить.
        :return: Список объектов Booking с загруженными данными о пользователе и общей суммы платежей.
        """
        now = datetime.now(timezone.utc)
        try:
            query = (
                select(
                    self.model,
                    func.sum(Pay.summ).label("total_payment")
                )
                    .join(self.model.user)           # JOIN для пользователя
                    .join(self.model.room)
                    .outerjoin(self.model.pays)     # LEFT JOIN для платежей
                    .filter(self.model.room_id == room_id, self.model.date_end >= now)
                    .group_by(self.model.id)         # Группировка по ID бронирования
                )

            result = await self._session.execute(query)
            rows = result.all()
            
            if rows:
                bookings = []
                for booking, total_payment in rows:
                    total = int(total_payment) if total_payment is not None else 0  # Если нет платежей → 0
                    bookings.append((booking, total))

                logger.info(f"Для комнаты №{room_id} найдено {len(bookings)} бронирований за указанный период")
                return bookings
            else:
                logger.info(f"Для комнаты №{room_id} нет бронирований за указанный период")
                return []
            
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении бронирований с деталями: {e}")
            return []

    async def complete_past_bookings(self):
        """
        Обновляет статус бронирований на 'completed', если дата и время бронирования уже прошли.
        """
        try:
            # Получаем текущее время
            now = datetime.now(timezone.utc)

            result = await self._session.execute(
                update(self.model)
                .where(
                    self.model.date_start < now.date(),           # Сравниваем DateTime полностью
                    self.model.status == "booked"
                )
                .values(status="completed")
            )
        
            # Получаем количество обновлённых строк
            updated_count = result.rowcount
        
            if updated_count > 0:
                await self._session.commit()
                logger.info(f"Обновлен статус для {updated_count} бронирований на 'completed'")
            else:
                logger.info("Нет бронирований для обновления статуса.")
                        
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при обновлении статуса бронирований: {e}")
            await self._session.rollback()
    
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

