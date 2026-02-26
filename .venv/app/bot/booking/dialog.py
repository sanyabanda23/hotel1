from aiogram_dialog import Dialog
from app.bot.booking.windows import (get_phone_nom_window, get_name_window, get_user_description_window, get_tg_nik_window,
                                     get_vk_url_window, get_confirmed_old_user_phone_window, get_confirmed_old_user_tg_window,
                                     get_confirmed_old_user_vk_window,
                                     get_confirmed_new_user_window, get_room_window, get_start_date_window, get_end_date_window,
                                     get_cost_window, get_confirmed_new_booking_window)

booking_dialog = Dialog(
    get_phone_nom_window(),
    get_tg_nik_window(),
    get_vk_url_window(),
    get_name_window(),
    get_user_description_window(),
    get_confirmed_new_user_window(),
    get_confirmed_old_user_phone_window(),
    get_confirmed_old_user_tg_window(),
    get_confirmed_old_user_vk_window(),
    get_room_window(),
    get_start_date_window(),
    get_end_date_window(),
    get_cost_window(),
    get_confirmed_new_booking_window()
)