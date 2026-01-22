from aiogram_dialog import DialogManager

async def get_confirmed_data_newuser(dialog_manager: DialogManager, **kwargs):
    """Получение данных для подтверждения внесения информации о госте в БД."""
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

async def get_confirmed_data_user(dialog_manager: DialogManager, **kwargs):
    """Получение данных для подтверждения информации 
    о госте? который ранее был внесен в БД."""
    user = dialog_manager.dialog_data['user']

    confirmed_text = (
        "<b>Гость с данным номером телефона</b>\n"
        f"<b>ранее проживал у нас!!!</b>\n"
        f"<b>Проверь информацию о нем!</b>\n\n"
        f"<b>📅 Подтверждение информации</b>\n\n"
        f"<b>🍴 Информация о госте:</b>\n"
        f"  - 👥 Имя гостя: {user_name}\n"
        f"  - 💻 Контактный телефон: {phone_nomber}\n"
        f"  - 📍ℹ️ Описание: {description_user}\n\n"
        "✅ Все ли верно?"
    )

    return {"confirmed_text": confirmed_text}

async def get_all_rooms(dialog_manager: DialogManager, **kwargs):
    """Получение списка номеров."""
    session = dialog_manager.middleware_data.get("session_without_commit")
    rooms = await RoomDAO(session).find_all()
    dialog_manager.dialog_data['rooms'] = rooms # обращение к хранилищу данных диалога в фреймворке
    return {"rooms": [room.to_dict() for room in rooms],
            "text_room": f'Всего найдено {len(rooms)} номеров. Выбери нужный по описанию'}

