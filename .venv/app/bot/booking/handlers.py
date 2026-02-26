from datetime import date
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Dialog
from aiogram_dialog.widgets.kbd import Button
from app.bot.booking.schemas import SNewUser, SNewBooking, UserPhoneFilter
from app.bot.booking.state import BookingState
from app.bot.admin.kbs import main_user_kb
from app.dao.dao import BookingDAO, UserDAO, RoomDAO

async def cancel_logic(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Сценарий бронирования отменен!")
    await callback.message.answer("Вы отменили сценарий бронирования.",
                                  reply_markup=main_user_kb(callback.from_user.id))

async def on_phone_input(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    """Обработчик ввода номера телефона и проверки номера среди пользователей."""
    session = dialog_manager.middleware_data.get("session_without_commit")
    
    # Очистка номера от лишних символов
    cleaned_phone = (
        message.text
        .replace(' ', '').replace('(', '').replace(')', '')
        .replace('-', '')
    )
    
    # Нормализация: +7 → 8 для РФ, +380 → 380 для Украины
    if cleaned_phone.startswith('+7'):
        cleaned_phone = '8' + cleaned_phone[2:]
    elif cleaned_phone.startswith('+380'):
        cleaned_phone = '380' + cleaned_phone[4:]
    
    # Проверка форматов: РФ (11 цифр, начинается с 8) или Украина (12 цифр, начинается с 380)
    is_russian = cleaned_phone.isdigit() and len(cleaned_phone) == 11 and cleaned_phone.startswith('8')
    is_ukrainian = cleaned_phone.isdigit() and len(cleaned_phone) == 12 and cleaned_phone.startswith('380')
    
    if not (is_russian or is_ukrainian):
        await message.answer(
            "Некорректный формат номера. "
            "Введите номер в формате:\n"
            "• +7ХХХХХХХХХХХ (Россия)\n"
            "• +380ХХХХХХХХХ (Украина)"
        )
        return  # Остаёмся в текущем состоянии
    
    find_model = UserPhoneFilter(phone_nom=cleaned_phone)
    user = await UserDAO(session).find_one_or_none(find_model)
    
    if user:
        dialog_manager.dialog_data["phone_nom"] = user.phone_nom
        await dialog_manager.switch_to(BookingState.check_nom)
    else:
        dialog_manager.dialog_data["phone_nom"] = cleaned_phone
        await dialog_manager.switch_to(BookingState.name)

async def on_name_input(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.dialog_data["name"] = message.text
    await dialog_manager.next()

async def on_description_user_input(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_manager.dialog_data["description_user"] = message.text
    await dialog_manager.next()

async def on_confirmation_user_yes(callback: CallbackQuery, widget, dialog_manager: DialogManager, **kwargs):
    """Обработчик внесения или обновления данных о госте."""
    session = dialog_manager.middleware_data.get("session_with_commit")

    # Получаем выбранные данные
    phone_nomber = dialog_manager.dialog_data['phone_nom']
    user_name = dialog_manager.dialog_data['name']
    description_user = dialog_manager.dialog_data['description_user']
    await callback.answer("Приступаю к сохранению")
    select_user = await UserDAO(session).find_one_or_none(UserPhoneFilter(phone_nom=phone_nomber))
    if select_user:
        filters_model = UserPhoneFilter(phone_nom=phone_nomber)
        values_model = SNewUser(username=user_name, phone_nom=phone_nomber, description=description_user)
        await UserDAO(session).update(filters=filters_model, values=values_model)
        await callback.answer(f"Информация о госте обновлена!")
    else:
        add_model = SNewUser(phone_nom=phone_nomber,
                               username=user_name, description=description_user)
        await UserDAO(session).add(add_model)
        await callback.answer(f"Гость успешно добавлен!")
    await dialog_manager.switch_to(BookingState.room)

async def on_confirmation_user_no(callback: CallbackQuery, dialog: Dialog, dialog_manager: DialogManager):
    await dialog_manager.switch_to(BookingState.phone_nom)

async def on_confirmation_chek_user_no(callback: CallbackQuery, dialog: Dialog, dialog_manager: DialogManager):
    await dialog_manager.switch_to(BookingState.name)

async def on_confirmation_check_user_yes(callback: CallbackQuery, dialog: Dialog, dialog_manager: DialogManager):
    await dialog_manager.switch_to(BookingState.room)

async def on_room_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, item_id: str):
    """Обработчик выбора номера."""
    session = dialog_manager.middleware_data.get("session_without_commit") # возвращает сессию, если она есть
    room_id = int(item_id)
    selected_room = await RoomDAO(session).find_one_or_none_by_id(room_id)
    dialog_manager.dialog_data["selected_room_id"] = selected_room.id
    dialog_manager.dialog_data["selected_room_description"] = selected_room.description
    await callback.answer(f"Выбран номер №{room_id}")
    await dialog_manager.switch_to(BookingState.booking_date_start)

async def process_date_start_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, selected_date: date):
    """Обработчик выбора даты заезда."""
    dialog_manager.dialog_data["booking_date_start"] = selected_date.isoformat()
    await dialog_manager.switch_to(BookingState.booking_date_end)

async def process_date_end_selected(callback: CallbackQuery, widget, dialog_manager: DialogManager, selected_date: date):
    """Обработчик выбора даты выезда."""
    session = dialog_manager.middleware_data.get("session_without_commit") # возвращает сессию, если она есть
    dialog_manager.dialog_data["booking_date_end"] = selected_date.isoformat()
    selected_date_start = dialog_manager.dialog_data["booking_date_start"]
    selected_room_id = int(dialog_manager.dialog_data["selected_room_id"])
    slots = await BookingDAO(session).check_available_bookings(room_id=selected_room_id, 
                                                               booking_date_start=selected_date_start, 
                                                               booking_date_end=selected_date.isoformat())
    if selected_date_start > selected_date.isoformat():
        await callback.message.answer(f"Дата заезда не может быть позже даты выезда!\n"
                                      f"Выбери период времени еще раз!")
        await dialog_manager.switch_to(BookingState.booking_date_start)
    else:
        if slots:
            await callback.answer(f"Выбрана дата: с {selected_date_start} по {selected_date}")
            await dialog_manager.switch_to(BookingState.cost)
        else:
            await callback.message.answer(f"В выбранный период с {selected_date_start} по {selected_date}\n"
                                          f"в номер №{selected_room_id} будет зянят!")
            await dialog_manager.switch_to(BookingState.booking_date_start)


async def on_cost_input(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    """Принимает информацию о стоимости проживания (с проверкой введения числа)"""
    user_input = message.text.strip()
    
    # Проверка: строка состоит только из цифр (целое число)
    if user_input.isdigit():
        # Преобразуем в число для дальнейших расчётов
        dialog_manager.dialog_data["cost"] = int(user_input)
        await dialog_manager.next()  # Переход к следующему шагу
    else:
        # Сообщение об ошибке + просьба повторить ввод
        await message.answer(
            'Ошибка: введите только число без букв и символов!\n'
            'Пример: 5000\n'
            'Попробуй ещё раз:'
        )
        
async def on_confirmation(callback: CallbackQuery, widget, dialog_manager: DialogManager, **kwargs):
    """Обработчик подтверждения бронирования."""
    session = dialog_manager.middleware_data.get("session_with_commit")
    
    # Получаем выбранные данные
    user = dialog_manager.dialog_data["user_id"]
    room = dialog_manager.dialog_data["selected_room_id"]
    date_start = dialog_manager.dialog_data["booking_date_start"]
    date_end = dialog_manager.dialog_data["booking_date_end"]
    cost = dialog_manager.dialog_data["cost"]
    check = await BookingDAO(session).check_available_bookings(room_id=room, 
                                                               booking_date_start=date_start, 
                                                               booking_date_end=date_end)
    if check:
        await callback.answer("Приступаю к сохранению")
        add_model = SNewBooking(user_id=user, room_id=room, date_start=date_start,
                                date_end=date_end, status="booked", cost=cost)
        await BookingDAO(session).add(add_model)
        await callback.answer(f"Бронирование успешно создано!")
        text = "Бронь успешно сохранена🔢!"
        await callback.message.answer(text, reply_markup=main_user_kb(callback.from_user.id))

        await dialog_manager.done() # завершает текущий диалог: удаляет его из стека задач и очищает контекст
    else:
        await callback.answer("Место на эти даты уже занято!")
        await dialog_manager.switch_to(BookingState.room)    


