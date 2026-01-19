from datetime import date
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from app.bot.booking.schemas import SNewUser, SNewBooking
from app.bot.user.kbs import main_user_kb
from app.dao.dao import BookingDAO, UserDAO, RoomDAO

async def cancel_logic(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer("Сценарий бронирования отменен!")
    await callback.message.answer("Вы отменили сценарий бронирования.",
                                  reply_markup=main_user_kb(callback.from_user.id))

async def on_phone_input(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    """Обработчик ввода номера телефона и проверки номера среди пользователей."""
    session = dialog_manager.middleware_data.get("session_without_commit")
    cleaned_phone = (
        message.text
        .replace(' ', '').replace('(', '').replace(')', '')
        .replace('+7', '8').replace('-', '')
    )
    
    # Проверка: 11 цифр, начинается с 8
    if not (cleaned_phone.isdigit() and len(cleaned_phone) == 11 and cleaned_phone.startswith('8')):
        await message.answer("Некорректный формат номера. Введите номер в формате +7ХХХХХХХХХХХ.")
        return  # Остаёмся в текущем состоянии
    
    dialog_manager.dialog_data["phone_nom"] = cleaned_phone
    dialog_manager.dialog_data["user"] = await UserDAO(session).find_one_or_none(SNewUser(phone_nom=cleaned_phone))
    if dialog_manager.dialog_data["user"]:
        await dialog_manager.switch_to(check_nom)
    else:
        await dialog_manager.switch_to(name)

async def on_name_input(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_managermanager.dialog_data["name"] = message.text
    await dialog_manager.next()

async def on_description_user_input(message: Message, dialog: Dialog, dialog_manager: DialogManager):
    dialog_managermanager.dialog_data["description_user"] = message.text
    await dialog_manager.next()

async def on_confirmation_user_yes(callback: CallbackQuery, widget, dialog_manager: DialogManager, **kwargs):
    """Обработчик внесения или обновления данных о госте."""
    session = dialog_manager.middleware_data.get("session_with_commit")

    # Получаем выбранные данные
    phone_nomber = dialog_manager.dialog_data['phone_nom']
    user_name = dialog_manager.dialog_data['name']
    description_user = dialog_manager.dialog_data['description_user']
    await callback.answer("Приступаю к сохранению")
    select_user = await UserDAO(session).find_one_or_none(SNewUser(phone_nom=phone_nomber))
    if select_user:
        filters_model = SNewUser(phone_nom=phone_nomber)
        values_model = SNewUser(name=user_name, description=description_user)
        await UserDAO(session).update(filters=filters_model, values=values_model)
        await callback.answer(f"Информация о госте обновлена!")
    else:
        add_model = SNewUser(phone_nom=phone_nomber,
                               name=user_name, description=description_user)
        await UserDAO(session).add(add_model)
        await callback.answer(f"Гость успешно добавлен!")
    await dialog_manager.next()

