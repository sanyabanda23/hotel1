from loguru import logger
from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup, CopyTextButton, InputMediaPhoto
from aiogram_dialog import DialogManager, StartMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.input_file import FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.booking.state import BookingState
from app.bot.my_bookings.state import MyBookingState
from app.bot.admin.state import OutputBookingsState, ClearState, FindUserState
from app.bot.admin.schemas import (SNewPay, SCheckUser, SCheckTgUser, SCheckVkUser, 
                                  UserFilter, SUpdatePhone, SUpdateName, SUpdateDescription,
                                  SUpdateVk, SUpdateTg)
from app.bot.admin.kbs import main_user_kb, cancel_pay_book_kb, clear_yes_no_kb, info_kb, update_user_kb
from app.config import settings
from app.dao.dao import UserDAO, BookingDAO, PayDAO, RoomDAO
from app.api.calendar_pgn import generate_calendar_report

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id

    media = []
    successful_generations = 0

    # Генерируем календари для room_id от 1 до 4
    for room_id in range(1, 5):
        try:
            if await generate_calendar_report(room_id=room_id):
                file_path = f'calendar_report_{room_id}.png'
                media.append(InputMediaPhoto(media=FSInputFile(file_path)))
                successful_generations += 1
                logger.info(f"Календарь для room_id={room_id} успешно сгенерирован и добавлен в медиагруппу")
            else:
                logger.warning(f"generate_calendar_report вернул False для room_id={room_id}")
        except FileNotFoundError:
            logger.error(f"Файл calendar_report_{room_id}.png не найден")
        except Exception as e:
            logger.error(f"Ошибка при генерации календаря для room_id={room_id}: {e}")

    # Отправляем медиагруппу, только если есть хотя бы одно фото
    if media:
        try:
            await message.answer_media_group(media=media)
            logger.info(f"Отправлено {successful_generations} календарей пользователю {user_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки медиагруппы: {e}")
            # Если отправка медиагруппы не удалась, отправляем сообщение об ошибке
            await message.answer("⚠️ Не удалось загрузить календари. Попробуйте позже.")
    else:
        logger.warning("Не удалось сгенерировать ни одного календаря для отправки")
        await message.answer("📅 Календари пока недоступны. Попробуйте позже.")

    # Отправляем приветственное сообщение
    welcome_text = (
        "👋 Добро пожаловать! 🏡\n\n"
        "Здесь ты сможешь организовать свою деятельность. 💡💼\n"
        "Используйте клавиатуру ниже, чтобы зарезервировать бронь и получить любую информацию! 📱"
    )
    await message.answer(text=welcome_text, reply_markup=main_user_kb(user_id))

### Реакция на кнопку Внести заявку на бронь
@router.callback_query(F.data == "book_room")
async def start_dialog_booking(call: CallbackQuery, dialog_manager: DialogManager, state: FSMContext):
    await call.answer("Бронирование номера")
    await dialog_manager.start(state=BookingState.phone_nom, mode=StartMode.RESET_STACK)

### Реакция на кнопку Мои брони
@router.callback_query(F.data == "my_bookings")
async def start_dialog_mybookings(call: CallbackQuery, dialog_manager: DialogManager, state: FSMContext):
    await call.answer("Формирование списка бронировваний")
    await state.set_state(OutputBookingsState.dialog_start)
    await dialog_manager.start(state=MyBookingState.room, mode=StartMode.RESET_STACK)

@router.callback_query(F.data == "no_output_book", OutputBookingsState.dialog_start)
async def no_output_bookings(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Сценарий вывода информации о бронях отменен!")
    await state.clear()
    await callback.message.answer("Вы отменили сценарий вывода информации о бронях.",
                                  reply_markup=main_user_kb(callback.from_user.id))

@router.callback_query(F.data.startswith("lastbooks_"), OutputBookingsState.dialog_start)
async def yes_output_last_bookings(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    selected_room = int(callback.data.split("_")[-1])   
    all_bookings = await BookingDAO(session_without_commit).get_bookings_with_details(room_id=int(selected_room))
    
    if not all_bookings:
        await callback.message.answer("Нет бронирований для отображения.", 
                                      reply_markup=main_user_kb(callback.from_user.id))
        await state.clear()
        return
    
    last_booking_id = all_bookings[-1][0].id
    home_page = False

    for book, total_payment in all_bookings:                                         
        # Форматируем дату и время для удобства чтения
        booking_date_start = book.date_start.strftime("%d.%m.%Y")  # День.Месяц.Год
        booking_date_end = book.date_end.strftime("%d.%m.%Y")
        booking_number = book.id
        booking_room = book.room_id
        booking_status = book.status
        booking_cost = book.cost
        booking_pay = total_payment
        booking_user = book.user.username
        phone_number = book.user.phone_nom
        tg_nik = book.user.tg_nik
        vk_url = book.user.vk_url
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
                        f"  - 📱 Контактный телефон: {phone_number}\n"
                        f"  - 💬 Ник в telegram: {tg_nik}\n"
                        f"  - 🌐 Профиль в ВК: {vk_url}\n"
                        f"  - 📝 Описание: {description}")
        if last_booking_id == booking_number:
            home_page = True
        await callback.message.answer(message_text, reply_markup=cancel_pay_book_kb(
                                                                    user_id=callback.from_user.id,
                                                                    book_id=booking_number, 
                                                                    home_page=home_page))
    await state.set_state(OutputBookingsState.books)

@router.callback_query(F.data.startswith("yearbooks_"), OutputBookingsState.dialog_start)
async def yes_output_all_bookings(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    selected_room = int(callback.data.split("_")[1])
    selected_year = int(callback.data.split("_")[2])
    all_bookings = await BookingDAO(session_without_commit).get_bookings_with_details_year(room_id=selected_room, year=selected_year)
    
    if not all_bookings:
        await callback.message.answer("Нет бронирований для отображения.", 
                                      reply_markup=main_user_kb(callback.from_user.id))
        await state.clear()
        return
    
    last_booking_id = all_bookings[-1][0].id
    home_page = False

    for book, total_payment in all_bookings:                                         
        # Форматируем дату и время для удобства чтения
        booking_date_start = book.date_start.strftime("%d.%m.%Y")  # День.Месяц.Год
        booking_date_end = book.date_end.strftime("%d.%m.%Y")
        booking_number = book.id
        booking_room = book.room_id
        booking_status = book.status
        booking_cost = book.cost
        booking_pay = total_payment
        booking_user = book.user.username
        phone_number = book.user.phone_nom
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
                        f"  - 📱 Контактный телефон: {phone_number}\n"
                        f"  - 📝 Описание: {description}")
        if last_booking_id == booking_number:
            home_page = True
        await callback.message.answer(message_text, reply_markup=cancel_pay_book_kb(
                                                                    user_id=callback.from_user.id,
                                                                    book_id=booking_number, 
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
    await call.message.answer('Укажи сумму платежа.')
    await state.set_state(OutputBookingsState.sum_pay)

@router.message(F.text, OutputBookingsState.sum_pay)
async def input_pay_booking(msg: Message, session_with_commit: AsyncSession, state: FSMContext):        
    await state.update_data(sum_pay=msg.text)
    data_pay = await state.get_data()
    add_model = SNewPay(summ=int(data_pay.get('sum_pay')), id_booking=int(data_pay.get('book_id')))
    await PayDAO(session_with_commit).add(add_model)
    text = f"Платеж {data_pay.get('sum_pay')}руб. добавлен к бронированию №{data_pay.get('book_id')}.💰"
    await msg.answer(text, reply_markup=main_user_kb(msg.from_user.id))
    await state.clear()

@router.callback_query(F.data == "back_home", OutputBookingsState.books)
async def back_home(call: CallbackQuery, state: FSMContext):
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
    from app.bot.create_bot import bot as b
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
async def copy_url_photo(call: CallbackQuery, session_without_commit: AsyncSession, state: FSMContext):
    rooms = await RoomDAO(session_without_commit).find_all()
    def room_url_kb(user_id: int) -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()

        if user_id in settings.ADMIN_IDS:
            for room in rooms:
                kb.add(InlineKeyboardButton(text=f"Номер №{room.id}", copy_text=CopyTextButton(text=room.url_photo)))
    
        kb.adjust(2)            # Устанавливает количество кнопок в одном ряду (строке) клавиатуры
        return kb.as_markup()
    text = "Выберите номер из списка ниже — ссылка на фотографии скопируется автоматически."
    await call.message.answer(text, reply_markup=room_url_kb(call.from_user.id))
    await call.answer()

### Реакция на вызов Отчеты
@router.callback_query(F.data == "info")
async def info(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    text = 'Добро пожаловать в раздел формирования отчётов!\n' \
           'С помощью кнопок ниже вы можете:'
    await callback.message.answer(text,
                                  reply_markup=info_kb(callback.from_user.id))

@router.callback_query(F.data == "back_home_info")
async def back_home_info(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('Главное меню', reply_markup=main_user_kb(call.from_user.id))

### Найти пользователя
@router.callback_query(F.data == "find_user")
async def check_user(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer('Введи контакт или имя гостя.')
    await state.set_state(FindUserState.input_info)

@router.message(F.text, FindUserState.input_info)
async def search_user(msg: Message, state: FSMContext, session_without_commit: AsyncSession):
    search_text = msg.text.strip()
    if not search_text:
        await msg.answer("Пожалуйста, введите данные для поиска.", reply_markup=info_kb(msg.from_user.id))
        return
    try:
        user_tg = await UserDAO(session_without_commit).find_one_or_none(SCheckTgUser(tg_nik=msg.text))
        user_vk = await UserDAO(session_without_commit).find_one_or_none(SCheckVkUser(vk_url=msg.text))
        cleaned_phone = (
        msg.text
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
    
        if is_russian or is_ukrainian:
            user = await UserDAO(session_without_commit).find_one_or_none(SCheckUser(phone_nom=cleaned_phone))
            if user:
                confirmed_text = (
                    f"<b>Информация о госте:</b>\n\n"
                    f"  - 🙋‍♂️ Имя гостя: {user.username}\n"
                    f"  - 💬 Ник в telegram: {user.tg_nik}\n"
                    f"  - 🌐 Профиль в ВК: {user.vk_url}\n"
                    f"  - 📱 Контактный телефон: {user.phone_nom}\n"
                    f"  - 📝 Описание: {user.description}\n")
                await msg.answer(confirmed_text, reply_markup=update_user_kb(user_id=msg.from_user.id,
                                                                             userbook_id=user.id,
                                                                             home_page=True))
                await state.set_state(FindUserState.select_user)
            else:
                await msg.answer("Гость с таким номером телефона не проживал!", reply_markup=info_kb(msg.from_user.id))
                await state.clear()
        elif user_tg:
            confirmed_text = (
                    f"<b>Информация о госте:</b>\n\n"
                    f"  - 🙋‍♂️ Имя гостя: {user_tg.username}\n"
                    f"  - 💬 Ник в telegram: {user_tg.tg_nik}\n"
                    f"  - 🌐 Профиль в ВК: {user_tg.vk_url}\n"
                    f"  - 📱 Контактный телефон: {user_tg.phone_nom}\n"
                    f"  - 📝 Описание: {user_tg.description}\n")
            await msg.answer(confirmed_text, reply_markup=update_user_kb(user_id=msg.from_user.id,
                                                                         userbook_id=user.id,
                                                                         home_page=True))
            await state.set_state(FindUserState.select_user)
        elif user_vk:
            confirmed_text = (
                    f"<b>Информация о госте:</b>\n\n"
                    f"  - 🙋‍♂️ Имя гостя: {user_vk.username}\n"
                    f"  - 💬 Ник в telegram: {user_vk.tg_nik}\n"
                    f"  - 🌐 Профиль в ВК: {user_vk.vk_url}\n"
                    f"  - 📱 Контактный телефон: {user_vk.phone_nom}\n"
                    f"  - 📝 Описание: {user_vk.description}\n")
            await msg.answer(confirmed_text, reply_markup=update_user_kb(user_id=msg.from_user.id,
                                                                         userbook_id=user.id,
                                                                         home_page=True))
            await state.set_state(FindUserState.select_user)
        else:
            users = await UserDAO(session_without_commit).find_all()
            id_users = []
            for user in users:
                if msg.text.lower() in user.username.lower():
                    id_users.append(user)
            if id_users:
                last_user_id = id_users[-1].id
                home_page = False

                for user in id_users:                                         
                    # Форматируем дату и время для удобства чтения
                    message_text = (
                        f"<b>Информация о госте:</b>\n\n"
                        f"  - 🙋‍♂️ Имя гостя: {user.username}\n"
                        f"  - 💬 Ник в telegram: {user.tg_nik}\n"
                        f"  - 🌐 Профиль в ВК: {user.vk_url}\n"
                        f"  - 📱 Контактный телефон: {user.phone_nom}\n"
                        f"  - 📝 Описание: {user.description}\n")
                    if last_user_id == user.id:
                        home_page = True
                    await msg.answer(message_text, reply_markup=update_user_kb(
                                                                    user_id=msg.from_user.id,
                                                                    userbook_id=user.id, 
                                                                    home_page=home_page))
                await state.set_state(FindUserState.select_user)
            else:
                message_text = "Такой гостя в базе отсутствует."
                await msg.answer(message_text, reply_markup=info_kb(msg.from_user.id))
                await state.clear()
    except Exception as e:
        logger.error(f"Ошибка при поиске пользователя: {e}")
        await msg.answer("Произошла ошибка при поиске. Попробуйте позже.", reply_markup=info_kb(msg.from_user.id))
        await state.clear()

@router.callback_query(F.data == "back_home_update")
async def back_home_update(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text('Главное меню', reply_markup=main_user_kb(call.from_user.id))

@router.callback_query(F.data.startswith("phone_user_"), FindUserState.select_user)
async def update_user_phone(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    selected_user = int(callback.data.split("_")[-1])
    await state.update_data(user_id=selected_user)
    await callback.message.answer('Укажи номер телефона гостя.')
    await state.set_state(FindUserState.update_phone)

@router.message(F.text, FindUserState.update_phone)
async def input_phone_user(msg: Message, session_with_commit: AsyncSession, state: FSMContext):        
    cleaned_phone = (
        msg.text
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
        await msg.answer(
            "Некорректный формат номера. "
            "Введите номер в формате:\n"
            "• +7ХХХХХХХХХХХ (Россия)\n"
            "• +380ХХХХХХХХХ (Украина)"
        )
        return  # Остаёмся в текущем состоянии
    
    update_model = SUpdatePhone(phone_nom=cleaned_phone)
    data = await state.get_data()
    search_filters = UserFilter(id=data.get('user_id'))
    await UserDAO(session_with_commit).update(filters=search_filters, values=update_model)
    await msg.answer("Информация о госте обновлена!")
    await state.set_state(FindUserState.select_user)

@router.callback_query(F.data.startswith("name_user_"), FindUserState.select_user)
async def update_user_name(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    selected_user = callback.data.split("_")[-1]
    await state.update_data(user_id=selected_user)
    await callback.message.answer('Укажи имя гостя.')
    await state.set_state(FindUserState.update_name)

@router.message(F.text, FindUserState.update_name)
async def input_name_user(msg: Message, session_with_commit: AsyncSession, state: FSMContext):        
    
    update_model = SUpdateName(username=msg.text)
    data = await state.get_data()
    search_filters = UserFilter(id=data.get('user_id'))
    await UserDAO(session_with_commit).update(filters=search_filters, values=update_model)
    await msg.answer("Информация о госте обновлена!")
    await state.set_state(FindUserState.select_user)

@router.callback_query(F.data.startswith("description_user_"), FindUserState.select_user)
async def update_user_description(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    selected_user = callback.data.split("_")[-1]
    await state.update_data(user_id=selected_user)
    await callback.message.answer('Предоставь новые описания гостя. Учти, старое описание будет удалено!')
    await state.set_state(FindUserState.update_description)

@router.message(F.text, FindUserState.update_description)
async def input_description_user(msg: Message, session_with_commit: AsyncSession, state: FSMContext):
    
    update_model = SUpdateDescription(description=msg.text)
    data = await state.get_data()
    search_filters = UserFilter(id=data.get('user_id'))
    await UserDAO(session_with_commit).update(filters=search_filters, values=update_model)
    await msg.answer("Информация о госте обновлена!")
    await state.set_state(FindUserState.select_user)

@router.callback_query(F.data.startswith("vk_user_"), FindUserState.select_user)
async def update_user_vk(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    selected_user = callback.data.split("_")[-1]
    await state.update_data(user_id=selected_user)
    await callback.message.answer('Укажи данные профиля в VK.')
    await state.set_state(FindUserState.update_vk)

@router.message(F.text, FindUserState.update_vk)
async def input_vk_user(msg: Message, session_with_commit: AsyncSession, state: FSMContext):
    
    update_model = SUpdateVk(vk_url=msg.text)
    data = await state.get_data()
    search_filters = UserFilter(id=data.get('user_id'))
    await UserDAO(session_with_commit).update(filters=search_filters, values=update_model)
    await msg.answer("Информация о госте обновлена!")
    await state.set_state(FindUserState.select_user)
    
@router.callback_query(F.data.startswith("tg_user_"), FindUserState.select_user)
async def update_user_tg(callback: CallbackQuery, state: FSMContext, session_without_commit: AsyncSession):
    selected_user = callback.data.split("_")[-1]
    await state.update_data(user_id=selected_user)
    await callback.message.answer('Укажи данные профиля в Telegram.')
    await state.set_state(FindUserState.update_tg)

@router.message(F.text, FindUserState.update_tg)
async def input_tg_user(msg: Message, session_with_commit: AsyncSession, state: FSMContext):        
    
    update_model = SUpdateTg(tg_nik=msg.text)
    data = await state.get_data()
    search_filters = UserFilter(id=data.get('user_id'))
    await UserDAO(session_with_commit).update(filters=search_filters, values=update_model)
    await msg.answer("Информация о госте обновлена!")
    await state.set_state(FindUserState.select_user)

