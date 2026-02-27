from loguru import logger
from app.bot.create_bot import bot
from app.config import settings
from app.dao.dao import BookingDAO, RoomDAO
from app.dao.database import async_session_maker
from typing import List, Tuple
from app.dao.models import Booking
from app.api.schemas import SNewRoom

async def disable_booking():
    async with async_session_maker() as session:
        await BookingDAO(session).complete_past_bookings()

async def send_admin_msg():
    async with async_session_maker() as session:
        check_in: List[Tuple[Booking, int]] = await BookingDAO(session).get_bookings_with_details_date_start()
        check_out: List[Tuple[Booking, int]] = await BookingDAO(session).get_bookings_with_details_date_end()

        # Функция для формирования сообщения
        def build_message(booking: Booking, total_payment: int, action: str) -> str:
            user = booking.user
            username = (user.username or "Не указано") if user else "Не указан"
            phone = (user.phone_nom or "Не указан") if user else "Не указан"
            tg_nik = (user.tg_nik or "Не указан") if user else "Не указан"
            vk_url = (user.vk_url or "Не указан") if user else "Не указан"
            description = (user.description or "Нет описания") if user else "Нет данных"


            date_start = booking.date_start.strftime("%d.%m.%Y")
            date_end = booking.date_end.strftime("%d.%m.%Y")


            if action == "check_in":
                header = f"<b>Сегодня заселяется номер №{booking.room_id}!</b>"
            else:
                header = f"<b>Завтра выезжают гости из номера №{booking.room_id}!</b>"

            return (
                f"{header}\n"
                f"<b>Бронь №{booking.id}:</b>\n\n"
                f"📅 <b>Дата:</b> с {date_start} по {date_end}\n"
                f"💰 Стоимость проживания: {booking.cost} рублей\n"
                f"💸 Внесена оплата: {total_payment} рублей\n"
                f"  - 👤 Имя гостя: {username}\n"
                f"  - 📱 Контактный телефон: {phone}\n"
                f"  - 💬 Ник в telegram: {tg_nik}\n"
                f"  - 🌐 Профиль в ВК: {vk_url}\n"
                f"  - 📝 Описание: {description}"
            )

        # Отправка сообщений о заездах
        if check_in:
            for booking, total_payment in check_in:
                message_text = build_message(booking, total_payment, "check_in")
                for admin_id in settings.ADMIN_IDS:
                    try:
                        await bot.send_message(admin_id, text=message_text, parse_mode="HTML")
                        logger.info(f"Сообщение о заселении №{booking.id} отправлено админу {admin_id}")
                    except Exception as e:
                        logger.error(f"Ошибка отправки сообщения о заселении №{booking.id} админу {admin_id}: {e}")
        else:
            message_text = "Сегодня гости не будут заезжать…\nБронирований на сегодня нет. 😢"
            for admin_id in settings.ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, text=message_text, parse_mode="HTML")
                    logger.info(f"Сообщение об отсутствии заездов отправлено админу {admin_id}")
                except Exception as e:
                    logger.error(f"Ошибка отправки сообщения об отсутствии заездов админу {admin_id}: {e}")

        # Отправка сообщений о выездах
        if check_out:
            for booking, total_payment in check_out:
                message_text = build_message(booking, total_payment, "check_out")
                for admin_id in settings.ADMIN_IDS:
                    try:
                        await bot.send_message(admin_id, text=message_text, parse_mode="HTML")
                        logger.info(f"Сообщение о выезде №{booking.id} отправлено админу {admin_id}")
                    except Exception as e:
                        logger.error(f"Ошибка отправки сообщения о выезде №{booking.id} админу {admin_id}: {e}")
        else:
            message_text = "Сегодня выселений не будет!"
            for admin_id in settings.ADMIN_IDS:
                try:
                    await bot.send_message(admin_id, text=message_text, parse_mode="HTML")
                    logger.info(f"Сообщение об отсутствии выездов отправлено админу {admin_id}")
                except Exception as e:
                    logger.error(f"Ошибка отправки сообщения об отсутствии выездов админу {admin_id}: {e}")

async def add_rooms():
    async with async_session_maker() as session:
        rooms = (("https://cloud.mail.ru/public/Q5ws/QbcLk4zvX", "Двухкомнатный номер люкс"),
                 ("https://cloud.mail.ru/public/xLwU/UX1tEgQb2","Однокомнатный номер в конце корридора слева"),
                 ("https://cloud.mail.ru/public/T5Ex/x7NxBoGig","Однокомнатный номер в конце корридора справа"),
                 ("https://cloud.mail.ru/public/RG6Z/sdMaMaSNZ","Однокомнатный номер справа"))
        for room in rooms:
            add_model = SNewRoom(url_photo=room[0], description=room[1])
            if await RoomDAO(session).add(add_model):
                logger.info(f"{room[1]} добавлен в базу данных")
            else:
                logger.info(f"{room[1]} не удалось добавить в базу данных")

async def show_rooms():
    async with async_session_maker() as session:
        rooms = await RoomDAO(session).find_all()
        if rooms:
            logger.info(f"Найдено {len(rooms)} записей")
            for room in rooms:
                logger.info(f"Комната №{room.id} с описаниием '{room.description}'")
        else:
            logger.info(f"Записи не найдены")