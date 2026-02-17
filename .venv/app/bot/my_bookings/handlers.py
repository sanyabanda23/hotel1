from datetime import date
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Button
from app.bot.booking.schemas import SNewUser, SNewBooking
from app.bot.my_bookings.state import MyBookingState
from app.bot.admin.state import OutputBookingsState
from app.bot.admin.kbs import main_user_kb, yes_no_kb_last_books, yes_no_kb_year_books
from app.dao.dao import BookingDAO, UserDAO, RoomDAO

async def cancel_logic(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Сценарий вывода информации о бронях отменен!")
    await callback.message.answer("Вы отменили сценарий вывода информации о бронях.",
                                  reply_markup=main_user_kb(callback.from_user.id))
    
async def on_room_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, item_id: str):
    """Обработчик выбора номера."""
    dialog_manager.dialog_data["selected_room"] = item_id
    await callback.answer(f"Выбран номер №{item_id}")
    await dialog_manager.next()

async def on_list_last_bookings(callback: CallbackQuery, dialog: Dialog, dialog_manager: DialogManager):
    session = dialog_manager.middleware_data.get("session_without_commit")
    selected_room = dialog_manager.dialog_data["selected_room"]
    all_bookings = await BookingDAO(session).get_bookings_with_details(room_id=int(selected_room))
    if all_bookings:
        text = f'Найдено {len(all_bookings)} записей!\n' \
               f'Вывести их?'
        await callback.message.answer(text, reply_markup=yes_no_kb_last_books(callback.from_user.id, selected_room))
        await dialog_manager.done()
    else:
        text = f'По номеру №{selected_room} отсутствует информация о бронированиях.'
        await callback.message.answer(text)
        await dialog_manager.switch_to(MyBookingState.room)

async def on_all_bookings(callback: CallbackQuery, dialog: Dialog, dialog_manager: DialogManager):
    await dialog_manager.switch_to(MyBookingState.year)


async def on_list_all_bookings(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    user_input = message.text.strip()
    
    # Проверка: строка состоит только из цифр (целое число)
    if user_input.isdigit():
        # Преобразуем в число для дальнейших расчётов
        session = dialog_manager.middleware_data.get("session_without_commit")
        selected_room = dialog_manager.dialog_data["selected_room"]
        all_bookings = await BookingDAO(session).get_bookings_with_details_year(
                                                            room_id=int(selected_room),
                                                            year=user_input
                                                            )
        if all_bookings:
            text = f'Найдено {len(all_bookings)} записей за {user_input} год.!\n' \
                   f'Вывести их?'
            await message.answer(text, reply_markup=yes_no_kb_year_books(message.from_user.id,
                                                                         selected_room,
                                                                         user_input))
            await dialog_manager.done()
        else:
            text = f'По номеру №{selected_room} отсутствует информация о бронированиях за {user_input} год.'
            await message.answer(text)
            await dialog_manager.switch_to(MyBookingState.room)
    else:
        # Сообщение об ошибке + просьба повторить ввод
        await message.answer(
            'Ошибка: введите только число без букв и символов!\n'
            'Пример: 2025\n'
            'Попробуй ещё раз:'
        )
    

    

