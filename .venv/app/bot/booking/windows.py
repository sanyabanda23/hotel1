from datetime import date, timedelta, timezone
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, ScrollingGroup, Select, Calendar, CalendarConfig, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from app.bot.booking.getters import (get_confirmed_data_newuser, get_confirmed_data_user, get_all_rooms,
                                     get_confirmed_data_booking)
from app.bot.booking.handlers import (cancel_logic, on_phone_input, on_name_input, on_description_user_input,
                                     on_confirmation_user_yes, on_confirmation_user_no, on_confirmation_chek_user_no,
                                     on_confirmation_chek_user_yes, on_room_selected, process_date_start_selected
                                     process_date_end_selected, on_cost_input, on_confirmation)
from app.bot.booking.state import BookingState

def get_phone_nom_window() -> Window: 
    Window(
        Const("Введите номер телефона гостя."),
        MessageInput(on_phone_input),
        Group(
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        state=BookingState.phone_nom
)

def get_name_window() -> Window: 
    Window(
        Const("Введите имя гостя."),
        MessageInput(on_name_input),
        Group(
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        state=BookingState.name
)

def get_user_description_window() -> Window: 
    Window(
        Const("Введите краткую информацию госте."),
        MessageInput(on_description_user_input),
        Group(
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        state=BookingState.description_user
)

