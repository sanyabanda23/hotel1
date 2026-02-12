from datetime import date, timedelta, timezone
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, ScrollingGroup, Select, Calendar, CalendarConfig, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from app.bot.booking.getters import (get_confirmed_data_newuser, get_confirmed_data_user, get_all_rooms,
                                     get_confirmed_data_booking)
from app.bot.booking.handlers import (cancel_logic, on_phone_input, on_name_input, on_description_user_input,
                                     on_confirmation_user_yes, on_confirmation_user_no, on_confirmation_chek_user_no,
                                     on_room_selected, process_date_start_selected,
                                     process_date_end_selected, on_cost_input, on_confirmation, on_confirmation_check_user_yes)
from app.bot.booking.state import BookingState

def get_phone_nom_window() -> Window:
    """Окно ввода телефона гостя.""" 
    return Window(
        Const("Введите номер телефона гостя."),
        MessageInput(on_phone_input),
        Group(
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        state=BookingState.phone_nom
)

def get_name_window() -> Window:
    """Окно ввода имени гостя.""" 
    return Window(
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
    """Окно ввода описания гостя.""" 
    return Window(
        Const("Введите краткую информацию о госте."),
        MessageInput(on_description_user_input),
        Group(
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        state=BookingState.description_user
)

def get_confirmed_old_user_window():
    """Окно подтверждения данных старого гостя."""
    return Window(
        Format("{confirmed_text}"),
        Group(
            Button(Const("Все верно"), id="confirm1", on_click=on_confirmation_check_user_yes),
            Button(Const("Нужно обновить информацию"), id="confirm2", on_click=on_confirmation_chek_user_no),
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
        ),
        state=BookingState.check_nom,
        getter=get_confirmed_data_user
    )

def get_confirmed_new_user_window():
    """Окно подтверждения данных нового гостя."""
    return Window(
        Format("{confirmed_text}"),
        Group(
            Button(Const("Все верно"), id="confirm1", on_click=on_confirmation_user_yes),
            Button(Const("Ввести данные заново"), id="confirm2", on_click=on_confirmation_user_no),
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
        ),
        state=BookingState.check_user,
        getter=get_confirmed_data_newuser
    )

def get_room_window() -> Window:
    """Окно выбора комнаты."""
    return Window(
        Format("{text_room}"),
        ScrollingGroup(                                             # группа с возможностью пагинации для больших списков
            Select(                                                 # специальный виджет для выбора из списка элементов.
                Format("Комната №{item[id]} - {item[description]}"),
                id="room_select",                                  # уникальный идентификатор виджета
                item_id_getter=lambda items: str(items["id"]),        # функция для получения ID каждого элемента
                items="rooms",                                     # имя ключа в данных, полученных из getter
                on_click=on_room_selected,
            ),
            id="rooms_scrolling",
            width=1,
            height=1,
        ),
        Group(
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        getter=get_all_rooms,
        state=BookingState.room,
    )

def get_start_date_window() -> Window:
    """Окно выбора даты заезда."""
    return Window(
        Const("Выбери дату заезда гостя"),
        Calendar(
            id="cal",
            on_click=process_date_start_selected,
            config=CalendarConfig(
                firstweekday=0,                             # указал что неделя у нас начинается с понедельника
                timezone=timezone(timedelta(hours=3)),      # установил московскую временную зону
                min_date=date.today()                       # установил минимальную дату брони
            )
        ),
        Back(Const("Назад")),
        Cancel(Const("Отмена"), on_click=cancel_logic),
        state=BookingState.booking_date_start,
    )

def get_end_date_window() -> Window:
    """Окно выбора даты выезда."""
    return Window(
        Const("Выбери дату выезда гостя"),
        Calendar(
            id="cal",
            on_click=process_date_end_selected,
            config=CalendarConfig(
                firstweekday=0,                             # указал что неделя у нас начинается с понедельника
                timezone=timezone(timedelta(hours=3)),      # установил московскую временную зону
                min_date=date.today()                       # установил минимальную дату брони
            )
        ),
        Back(Const("Назад")),
        Cancel(Const("Отмена"), on_click=cancel_logic),
        state=BookingState.booking_date_end,
    )

def get_cost_window() -> Window:
    """Окно ввода стоимости проживания.""" 
    return Window(
        Const("Введите стоимость проживания за весь период."),
        MessageInput(on_cost_input),
        Group(
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        state=BookingState.cost
)

def get_confirmed_new_booking_window():
    """Окно подтверждения данных бронирования."""
    return Window(
        Format("{confirmed_text}"),
        Group(
            Button(Const("Все верно"), id="confirm", on_click=on_confirmation),
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
        ),
        state=BookingState.confirmation,
        getter=get_confirmed_data_booking
    )