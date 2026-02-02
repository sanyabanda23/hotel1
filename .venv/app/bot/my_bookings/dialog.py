from aiogram_dialog import Dialog
from app.bot.my_bookings.windows import (get_room_window, get_all_or_last_bookings_window, get_year_window)

list_bookings_dialog = Dialog(
    get_room_window(),
    get_all_or_last_bookings_window(),
    get_year_window()
)