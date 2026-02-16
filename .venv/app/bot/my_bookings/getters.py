from aiogram_dialog import DialogManager
from app.dao.dao import BookingDAO, UserDAO, RoomDAO
from app.bot.booking.schemas import SNewUser, SNewBooking

async def get_all_rooms(dialog_manager: DialogManager, **kwargs):
    """Получение списка номеров."""
    session = dialog_manager.middleware_data.get("session_without_commit")
    rooms = await RoomDAO(session).find_all()
    return {"rooms": [room.to_dict() for room in rooms],
            "text_room": f'Всего найдено {len(rooms)} номеров. Выбери нужный по описанию'}

async def get_one_room(dialog_manager: DialogManager, **kwargs):
    """Получение инфы о номере."""
    room = dialog_manager.dialog_data['selected_room']
    return {"room": room}
