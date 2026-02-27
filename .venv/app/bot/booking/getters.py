from aiogram_dialog import DialogManager
from app.dao.dao import BookingDAO, UserDAO, RoomDAO
from app.bot.booking.schemas import UserPhoneFilter, UserTgNikFilter, UserVkUrlFilter
from datetime import datetime

async def get_confirmed_data_newuser(dialog_manager: DialogManager, **kwargs):
    """Получение данных для подтверждения внесения информации о госте в БД."""
    phone_number = dialog_manager.dialog_data['phone_nom']
    tg_nik = dialog_manager.dialog_data['tg_nik']
    vk_url = dialog_manager.dialog_data['vk_url']
    user_name = dialog_manager.dialog_data['name']
    description_user = dialog_manager.dialog_data['description_user']

    confirmed_text = (
    "<b>📅 Подтверждение информации</b>\n\n"
    f"<b>Информация о госте:</b>\n"
    f"  - 🙋‍♂️ Имя гостя: {user_name}\n"
    f"  - 📱 Контактный телефон: {phone_number}\n"
    f"  - 💬 Ник в telegram: {tg_nik}\n"
    f"  - 🌐 Профиль в ВК: {vk_url}\n"
    f"  - 📝 Описание: {description_user}\n\n"
    "✅ Всё ли верно?"
    )


    return {"confirmed_text": confirmed_text}

async def get_confirmed_data_user_phone(dialog_manager: DialogManager, **kwargs):
    """Получение данных для подтверждения информации 
    о госте? который ранее был внесен в БД."""
    session = dialog_manager.middleware_data.get("session_without_commit")
    user_phone = dialog_manager.dialog_data['phone_nom']
    find_model = UserPhoneFilter(phone_nom=user_phone)
    user = await UserDAO(session).find_one_or_none(find_model)

    confirmed_text = (
        "<b>Гость с данным номером телефона</b>\n"
        f"<b>уже зарегистрирован в базе!!!</b>\n"
        f"<b>Проверь информацию о нем!</b>\n\n"
        f"<b>📅 Подтверждение информации</b>\n\n"
        f"<b>Информация о госте:</b>\n"
        f"  - 🙋‍♂️ Имя гостя: {user.username}\n"
        f"  - 💬 Ник в telegram: {user.tg_nik}\n"
        f"  - 🌐 Профиль в ВК: {user.vk_url}\n"
        f"  - 📱 Контактный телефон: {user.phone_nom}\n"
        f"  - 📝 Описание: {user.description}\n\n"
        "✅ Все ли верно?"
    )

    return {"confirmed_text": confirmed_text}

async def get_confirmed_data_user_tg(dialog_manager: DialogManager, **kwargs):
    """Получение данных для подтверждения информации 
    о госте? который ранее был внесен в БД."""
    session = dialog_manager.middleware_data.get("session_without_commit")
    user_tg = dialog_manager.dialog_data['tg_nik']
    find_model = UserTgNikFilter(tg_nik=user_tg)
    user = await UserDAO(session).find_one_or_none(find_model)

    confirmed_text = (
        "<b>Гость с данным номером телефона</b>\n"
        f"<b>уже зарегистрирован в базе!!!</b>\n"
        f"<b>Проверь информацию о нем!</b>\n\n"
        f"<b>📅 Подтверждение информации</b>\n\n"
        f"<b>Информация о госте:</b>\n"
        f"  - 🙋‍♂️ Имя гостя: {user.username}\n"
        f"  - 💬 Ник в telegram: {user.tg_nik}\n"
        f"  - 🌐 Профиль в ВК: {user.vk_url}\n"
        f"  - 📱 Контактный телефон: {user.phone_nom}\n"
        f"  - 📝 Описание: {user.description}\n\n"
        "✅ Все ли верно?"
    )

    return {"confirmed_text": confirmed_text}

async def get_confirmed_data_user_vk(dialog_manager: DialogManager, **kwargs):
    """Получение данных для подтверждения информации 
    о госте? который ранее был внесен в БД."""
    session = dialog_manager.middleware_data.get("session_without_commit")
    user_vk = dialog_manager.dialog_data['vk_url']
    find_model = UserVkUrlFilter(vk_url=user_vk)
    user = await UserDAO(session).find_one_or_none(find_model)

    confirmed_text = (
        "<b>Гость с данным номером телефона</b>\n"
        f"<b>уже зарегистрирован в базе!!!</b>\n"
        f"<b>Проверь информацию о нем!</b>\n\n"
        f"<b>📅 Подтверждение информации</b>\n\n"
        f"<b>Информация о госте:</b>\n"
        f"  - 🙋‍♂️ Имя гостя: {user.username}\n"
        f"  - 💬 Ник в telegram: {user.tg_nik}\n"
        f"  - 🌐 Профиль в ВК: {user.vk_url}\n"
        f"  - 📱 Контактный телефон: {user.phone_nom}\n"
        f"  - 📝 Описание: {user.description}\n\n"
        "✅ Все ли верно?"
    )

    return {"confirmed_text": confirmed_text}

async def get_all_rooms(dialog_manager: DialogManager, **kwargs):
    """Получение списка номеров."""
    session = dialog_manager.middleware_data.get("session_without_commit")
    rooms = await RoomDAO(session).find_all()
    return {"rooms": [room.to_dict() for room in rooms],
            "text_room": f'Всего найдено {len(rooms)} номеров. Выбери нужный по описанию'}

async def get_confirmed_data_booking(dialog_manager: DialogManager, **kwargs):
    """Получение данных для подтверждения бронирования."""
    session = dialog_manager.middleware_data.get("session_without_commit")
    
    search_filters = []
    if dialog_manager.dialog_data["phone_nom"] != "отсутствует":
        search_filters.append(UserPhoneFilter(phone_nom=dialog_manager.dialog_data["phone_nom"]))
    elif dialog_manager.dialog_data["tg_nik"] != "отсутствует":
        search_filters.append(UserTgNikFilter(tg_nik=dialog_manager.dialog_data["tg_nik"]))
    elif dialog_manager.dialog_data["vk_url"] != "отсутствует":
        search_filters.append(UserVkUrlFilter(vk_url=dialog_manager.dialog_data["vk_url"]))


        # Ищем пользователя по каждому фильтру в порядке приоритета
    for filter_model in search_filters:
            user = await UserDAO(session).find_one_or_none(filter_model)
            if user:
                print(f"Нашел пользователя №{user.id}")
                break
            else:
                print("В этот раз не получилось")
            

    dialog_manager.dialog_data["user_id"] = user.id
    selected_room_id = dialog_manager.dialog_data["selected_room_id"]
    date_start = dialog_manager.dialog_data["booking_date_start"]
    date_end = dialog_manager.dialog_data["booking_date_end"]
    cost = dialog_manager.dialog_data["cost"]
    date_st = datetime.strptime(date_start, "%Y-%m-%d").strftime("%d.%m.%Y")
    date_en = datetime.strptime(date_end, "%Y-%m-%d").strftime("%d.%m.%Y")

    confirmed_text = (
        "<b>📅 Подтверждение бронирования</b>\n\n"
        f"<b>📆 Дата:</b>с {date_st} по {date_en}\n\n"
        f"<b>Информация о бронировании:</b>\n"
        f"  - 🙋‍♂️ Имя гостя: {user.username}\n"
        f"  - 💬 Ник в telegram: {user.tg_nik}\n"
        f"  - 🌐 Профиль в ВК: {user.vk_url}\n"
        f"  - 📱 Контактный телефон: {user.phone_nom}\n"
        f"  - 📝 Описание: {user.description}\n"
        f"  - 📍 Номер: <b>{selected_room_id}</b>\n"
        f"  - 👥 Стоимость проживания: {cost}\n\n"
        "✅ Все ли верно?"
    )

    return {"confirmed_text": confirmed_text}

