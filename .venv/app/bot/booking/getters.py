from aiogram_dialog import DialogManager

async def get_confirmed_data_user(dialog_manager: DialogManager, **kwargs):
    """Получение данных для подтверждения бронирования."""
    phone_nomber = dialog_manager.dialog_data['phone_nom']
    user_name = dialog_manager.dialog_data['name']
    description_user = dialog_manager.dialog_data['description_user']

    confirmed_text = (
        "<b>📅 Подтверждение информации</b>\n\n"
        f"<b>🍴 Информация о госте:</b>\n"
        f"  - 👥 Имя гостя: {user_name}\n"
        f"  - 💻 Контактный телефон: {phone_nomber}\n"
        f"  - 📍ℹ️ Описание: {description_user}\n\n"
        "✅ Все ли верно?"
    )

    return {"confirmed_text": confirmed_text}