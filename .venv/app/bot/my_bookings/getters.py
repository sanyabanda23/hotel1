from aiogram_dialog import DialogManager
from app.dao.dao import BookingDAO, UserDAO, RoomDAO
from app.bot.booking.schemas import SNewUser, SNewBooking

async def get_all_rooms(dialog_manager: DialogManager, **kwargs):
    """Получение списка номеров."""
    session = dialog_manager.middleware_data.get("session_without_commit")
    rooms = await RoomDAO(session).find_all()
    dialog_manager.dialog_data['rooms'] = rooms # обращение к хранилищу данных диалога в фреймворке
    return {"rooms": [room.to_dict() for room in rooms],
            "text_room": f'Всего найдено {len(rooms)} номеров. Выбери нужный по описанию'}

async def get_all_last_bookings(dialog_manager: DialogManager, **kwargs):
    """Получение списка номеров."""
    bookings = dialog_manager.dialog_data["last_bookings"]
    booking_texts = []
    for book in bookings:                                          # enumerate(user_bookings) в Python преобразует итерируемый объект в итератор пар «индекс — элемент»
        # Форматируем дату и время для удобства чтения
        booking_date_start = book.date_start.strftime("%d.%m.%Y")  # День.Месяц.Год
        booking_date_end = book.date_end.strftime("%d.%m.%Y")
        booking_number = book.id
        booking_room = book.room_id
        booking_status = book.status
        booking_cost = book.cost
        booking_pay = book.total_payment
        booking_user = book.user.username
        phone_nomber = book.user.phone_nom
        description = book.user.description
        if booking_status == "booked":
            status_text = "Забронирован"
        elif booking_status == "completed":
            status_text = "Исполнено"
        message_text = (f"<b>Бронь №{booking_number} номера {booking_room}:</b>\n\n"
                        f"📅 <b>Дата:</b> с {booking_date_start} по {booking_date_end}\n"
                        f"📌 <b>Статус:</b> {status_text}\n"
                        f"Стоимость проживания: {booking_cost} рублей\n"
                        f"Внесена оплата: {booking_pay} рублей\n"
                        f"  - 👥 Имя гостя: {booking_user}\n"
                        f"  - 💻 Контактный телефон: {phone_nomber}\n"
                        f"  - 📍ℹ️ Описание: {description}")
        booking_texts.append(message_text)
    
    return {"bookings": [booking.to_dict() for booking in bookings],
            "text_book": [text.to_dict() for text in booking_texts]}