from datetime import date
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Button
from app.bot.booking.schemas import SNewUser, SNewBooking
from app.bot.my_bookings.state import MyBookingState
from app.bot.admin.kbs import main_user_kb
from app.dao.dao import BookingDAO, UserDAO, RoomDAO

async def cancel_logic(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Сценарий вывода информации о бронях отменен!")
    await callback.message.answer("Вы отменили сценарий вывода информации о бронях.",
                                  reply_markup=main_user_kb(callback.from_user.id))
    
async def on_room_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, item_id: str):
    """Обработчик выбора номера."""
    session = dialog_manager.middleware_data.get("session_without_commit") # возвращает сессию, если она есть
    room_id = int(item_id)
    selected_room = await RoomDAO(session).find_one_or_none_by_id(room_id)
    dialog_manager.dialog_data["selected_room"] = selected_room
    await callback.answer(f"Выбран номер №{room_id}")
    await dialog_manager.next()

async def on_list_last_bookings(callback: CallbackQuery, dialog: Dialog, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data.get("session_without_commit")
    selected_room = dialog_manager.dialog_data["selected_room"]
    dialog_manager.dialog_data["last_bookings"] = await BookingDAO(session).get_bookings_with_details(selected_room.id)
    await dialog_manager.switch_to(MyBookingState.last)

async def on_list_all_bookings(callback: CallbackQuery, dialog: Dialog, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MyBookingState.year)

async def on_list_last_bookings(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    user_input = message.text.strip()
    
    # Проверка: строка состоит только из цифр (целое число)
    if user_input.isdigit():
        # Преобразуем в число для дальнейших расчётов
        session = dialog_manager.middleware_data.get("session_without_commit")
        dialog_manager.dialog_data["year"] = int(user_input)
        selected_room = dialog_manager.dialog_data["selected_room"]
        dialog_manager.dialog_data["all_bookings"] = await BookingDAO(session).get_bookings_with_details_year(
                                                            room_id=selected_room.id,
                                                            year=dialog_manager.dialog_data["year"]
                                                            )
        await dialog_manager.switch_to(MyBookingState.all_in_year)
    else:
        # Сообщение об ошибке + просьба повторить ввод
        await message.answer(
            'Ошибка: введите только число без букв и символов!\n'
            'Пример: 2025\n'
            'Попробуй ещё раз:'
        )
    

    

