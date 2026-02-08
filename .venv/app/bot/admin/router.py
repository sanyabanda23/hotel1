from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.booking.state import BookingState
from app.bot.my_bookings.state import MyBookingState
from app.bot.admin.state import OutputBookingsState, ClearState
from app.bot.admin.schemas import SNewPay
from app.bot.admin.kbs import main_user_kb, cancel_pay_book_kb, clear_yes_no_kb
from app.config import settings
from app.dao.dao import UserDAO, BookingDAO, PayDAO

router = Router()
from app.bot.create_bot import bot as b

@router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    text = ("👋 Добро пожаловать! 🏡\n\n"
        "Здесь ты сможешь организовать свою деятельность. 💡💼\n"
        "Используйте клавиатуру ниже, чтобы зарезервировать бронь и получить любую информацию! 📱")
    await message.answer(text, reply_markup=main_user_kb(user_id))

### Реакция на кнопку Внести заявку на бронь
@router.callback_query(F.data == "book_room")
async def start_dialog_booking(call: CallbackQuery, dialog_manager: DialogManager, state: FSMContext):
    await call.answer("Бронирование номера")
    await dialog_manager.start(state=BookingState.phone_nom, mode=StartMode.RESET_STACK)

### Реакция на кнопку Мои брони
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

@router.callback_query(F.data.startswith("dell_book_"), OutputBookingsState.books)
async def delete_booking(call: CallbackQuery, session_with_commit: AsyncSession, state: FSMContext):
    book_id = int(call.data.split("_")[-1])
    await BookingDAO(session_with_commit).delete_book(book_id)
    await call.answer("Запись о брони удалена!", show_alert=True)
    await call.message.delete()        # Асинхронный метод, отправляющий запрос к API Telegram на удаление сообщения

@router.callback_query(F.data.startswith("pay_book_"), OutputBookingsState.books)
async def summ_pay_booking(call: CallbackQuery, state: FSMContext):
    book_id = int(call.data.split("_")[-1])
    await state.update_data(book_id=book_id)
    await call.message.answer('Укажи сумму плтежа.')
    await state.set_state(OutputBookingsState.sum_pay)

@router.message(F.text, OutputBookingsState.sum_pay)
async def input_pay_booking(msg: Message, session_with_commit: AsyncSession, state: FSMContext):        
    await state.update_data(sum_pay=msg.text)
    data_pay = await state.get_data()
    add_model = SNewPay(summ=int(data_pay.get('sum_pay')), id_booking=int(data_pay.get('book_id')))
    await PayDAO(session_with_commit).add(add_model)
    text = f'Платеж {data_pay.get('sum_pay')}руб. добавлен к бронированию №{data_pay.get('book_id')}.💰'
    await msg.answer(text, reply_markup=main_user_kb(msg.from_user.id))
    await state.clear()

@router.callback_query(F.data == "back_home", OutputBookingsState.books)
async def delete_booking(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Главное меню', reply_markup=main_user_kb(call.from_user.id))

### Удаление сообщение из чата
@router.callback_query(F.data == 'clear_chat')
async def cmd_clear(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Удалить сообщения из чата?', reply_markup=clear_yes_no_kb)
    await state.set_state(ClearState.delete)

@router.message(F.text == 'Да', ClearState.delete)
async def delete_msg(msg: Message, state: FSMContext):
    await state.update_data(delete=msg.text)
    try:  
        # Все сообщения, начиная с текущего и до первого (message_id = 0)  
        for i in range(msg.message_id, 0, -1):  
            await b.delete_message(msg.from_user.id, i)
        await msg.edit_reply_markup(reply_markup=None)
        await state.clear()  
    except TelegramBadRequest as ex:  
        # Если сообщение не найдено (уже удалено или не существует), код ошибки — «Bad Request: message to delete not found»  
        if ex.message == 'Bad Request: message to delete not found':
            await state.clear()  
            print("Все сообщения удалены")

@router.message(F.text == 'Нет', ClearState.delete)
async def delete_msg(msg: Message, state: FSMContext):
    await msg.edit_reply_markup(reply_markup=None)
    await state.clear()

### Реакция на кнопку Ссылка на фото номеров
@router.callback_query(F.data == "url_photo")
async def copy_url_photo(call: CallbackQuery, state: FSMContext):
    