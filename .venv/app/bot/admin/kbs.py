from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.config import settings

def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if user_id in settings.ADMIN_IDS:
        kb.add(InlineKeyboardButton(text="📋 Внести заявку на бронь", callback_data="book_room"))
        kb.add(InlineKeyboardButton(text="📅 Мои брони", callback_data="my_bookings"))
        kb.add(InlineKeyboardButton(text="🕵️‍♂️ Найти гостя", callback_data="find_user"))
        kb.add(InlineKeyboardButton(text="📷 Ссылка на фото номеров", callback_data="url_photo"))
        kb.add(InlineKeyboardButton(text="🧹 Очистить чат", callback_data='clear_chat'))
        kb.add(InlineKeyboardButton(text="📊 Отчеты", callback_data="info"))
    
    kb.adjust(1)            # Устанавливает количество кнопок в одном ряду (строке) клавиатуры
    return kb.as_markup()

def yes_no_kb_last_books(user_id: int, room_id: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if user_id in settings.ADMIN_IDS:
        kb.add(InlineKeyboardButton(text="✅ Да", callback_data=f"lastbooks_{room_id}"))
        kb.add(InlineKeyboardButton(text="❌ Отменить", callback_data="no_output_book"))
    
    kb.adjust(1)            # Устанавливает количество кнопок в одном ряду (строке) клавиатуры
    return kb.as_markup()

def yes_no_kb_year_books(user_id: int, room_id: str, year: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if user_id in settings.ADMIN_IDS:
        kb.add(InlineKeyboardButton(text="✅ Да", callback_data=f"yearbooks_{room_id}_{year}"))
        kb.add(InlineKeyboardButton(text="❌ Отменить", callback_data="no_output_book"))
    
    kb.adjust(1)            # Устанавливает количество кнопок в одном ряду (строке) клавиатуры
    return kb.as_markup()

def cancel_pay_book_kb(user_id: int, book_id: int, home_page: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    if user_id in settings.ADMIN_IDS:
        kb.add(InlineKeyboardButton(text="Добавить платеж", callback_data=f"pay_book_{book_id}"))
        kb.add(InlineKeyboardButton(text="Удалить запись", callback_data=f"dell_book_{book_id}"))
        if home_page:
            kb.add(InlineKeyboardButton(text="🏠 На главную", callback_data="back_home"))
    kb.adjust(1)
    return kb.as_markup()

clear_yes_no_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Да")], 
                                                [KeyboardButton(text="Нет")]], 
                                                one_time_keyboard=True, resize_keyboard=True)

def info_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    if user_id in settings.ADMIN_IDS:
        kb.add(InlineKeyboardButton(text="Проверить гостя", callback_data=f"check_user"))
        kb.add(InlineKeyboardButton(text="🏠 На главную", callback_data="back_home_info"))
    kb.adjust(1)
    return kb.as_markup()

def update_user_kb(user_id: int, userbook_id: int, home_page: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    
    if user_id in settings.ADMIN_IDS:
        kb.add(InlineKeyboardButton(text="Изменить имя гостя", callback_data=f"name_user_{userbook_id}"))
        kb.add(InlineKeyboardButton(text="Обновить описание гостя", callback_data=f"description_user_{userbook_id}"))
        kb.add(InlineKeyboardButton(text="Обновить номер телефона", callback_data=f"phone_user_{userbook_id}"))
        kb.add(InlineKeyboardButton(text="Обновить профиль в Vk", callback_data=f"vk_user_{userbook_id}"))
        kb.add(InlineKeyboardButton(text="Обновить контакт в Telegram", callback_data=f"tg_user_{userbook_id}"))
        if home_page:
            kb.add(InlineKeyboardButton(text="🏠 На главную", callback_data="back_home_update"))
    kb.adjust(1)
    return kb.as_markup()