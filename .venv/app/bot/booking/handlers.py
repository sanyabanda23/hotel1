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

