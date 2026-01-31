from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.booking.state import BookingState
from app.bot.admin.kbs import main_user_kb
from app.config import settings
from app.dao.dao import UserDAO, BookingDAO

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    text = ("👋 Добро пожаловать! 🏠\n\nЗдесь ты сможешь организовать свою деятельность. 😋💻\n"
            "Используйте клавиатуру ниже, чтобы зарезервировать бронь и получить любую информацию! 🔢")
    await message.answer(text, reply_markup=main_user_kb(user_id))

@router.callback_query(F.data == "book_room")
async def start_dialog(call: CallbackQuery, dialog_manager: DialogManager):
    await call.answer("Бронирование номера")
    await dialog_manager.start(state=BookingState.phone_nom, mode=StartMode.RESET_STACK)

