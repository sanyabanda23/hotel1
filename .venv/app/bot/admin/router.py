from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.booking.state import BookingState
from app.bot.my_bookings.state import MyBookingState
from app.bot.admin.state import OutputBookingsState
from app.bot.admin.kbs import main_user_kb, cancel_pay_book_kb
from app.config import settings
from app.dao.dao import UserDAO, BookingDAO

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    text = ("👋 Добро пожаловать! 🏡\n\n"
        "Здесь ты сможешь организовать свою деятельность. 💡💼\n"
        "Используйте клавиатуру ниже, чтобы зарезервировать бронь и получить любую информацию! 📱")
    await message.answer(text, reply_markup=main_user_kb(user_id))


@router.callback_query(F.data == "book_room")
async def start_dialog_booking(call: CallbackQuery, dialog_manager: DialogManager, state: FSMContext):
    await call.answer("Бронирование номера")
    await dialog_manager.start(state=BookingState.phone_nom, mode=StartMode.RESET_STACK)


@router.callback_query(F.data == "my_bookings")
async def start_dialog_mybookings(call: CallbackQuery, dialog_manager: DialogManager, state: FSMContext):
    await call.answer("Формирование списка бронировваний")
    await dialog_manager.start(state=MyBookingState.room, mode=StartMode.RESET_STACK)

@router.callback_query(F.data == "no_output_book", OutputBookingsState.dialog_start)
async def no_output_bookings(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Сценарий вывода информации о бронях отменен!")
    await state.clear()
    await callback.message.answer("Вы отменили сценарий вывода информации о бронях.",
                                  reply_markup=main_user_kb(callback.from_user.id))

@router.callback_query(F.data == "yes_output_book", OutputBookingsState.dialog_start)
async def yes_output_bookings(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    all_bookings = data.get("all")
    for book in all_bookings:                                         
        # Форматируем дату и время для удобства чтения
        booking_date_start = book.date_start.strftime("%d.%m.%Y")  # День.Месяц.Год
        booking_date_end = book.date_end.strftime("%d.%m.%Y")
        booking_number = book.id
        booking_room = book.room_id
        booking_status = book.status
        booking_cost = book.cost
        booking_pay = book.total_payment
        booking_user = book.user.username
        phone_nomber = book.user.phone_nom
        description = book.user.description
        if booking_status == "booked":
            status_text = "Забронирован"
        elif booking_status == "completed":
            status_text = "Исполнено"
        message_text = (f"<b>Бронь №{booking_number} номера {booking_room}:</b>\n\n"
                        f"📅 <b>Дата:</b> с {booking_date_start} по {booking_date_end}\n"
                        f"📌 <b>Статус:</b> {status_text}\n"
                        f"💰 Стоимость проживания: {booking_cost} рублей\n"
                        f"💸 Внесена оплата: {booking_pay} рублей\n"
                        f"  - 👤 Имя гостя: {booking_user}\n"
                        f"  - 📱 Контактный телефон: {phone_nomber}\n"
                        f"  - 📝 Описание: {description}")
        if all_bookings[-1].id == booking_number:
            home_page = True
        await callback.message.answer(message_text, reply_markup=cancel_pay_book_kb(
                                                                    user_id=callback.from_user.id,
                                                                    book_id=book.id, 
                                                                    home_page=home_page))
    await state.set_state(OutputBookingsState.books)



        