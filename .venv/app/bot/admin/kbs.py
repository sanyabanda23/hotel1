from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from app.config import settings

def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if user_id in settings.ADMIN_IDS:
        kb.add(InlineKeyboardButton(text="🏠 Внести заявку на бронь", callback_data="book_room"))
        kb.add(InlineKeyboardButton(text="📅 Мои брони", callback_data="my_bookings"))
        kb.add(InlineKeyboardButton(text="ℹ️ Ссылка на фото номеров", callback_data="url_photo"))
        kb.add(InlineKeyboardButton(text="❌Очистить чат", callback_data='clear_chat'))
        kb.add(InlineKeyboardButton(text="🔐 Отчеты", callback_data="info"))
    
    kb.adjust(1)            # Устанавливает количество кнопок в одном ряду (строке) клавиатуры
    return kb.as_markup()