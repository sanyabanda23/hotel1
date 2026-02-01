from datetime import date, timedelta, timezone
from aiogram_dialog import Window
from aiogram_dialog.widgets.kbd import Button, Group, ScrollingGroup, Select, Calendar, CalendarConfig, Back, Cancel
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.input import MessageInput
from app.bot.my_bookings.getters import (get_all_rooms, get_all_last_bookings,
                                     get_confirmed_data_booking)
from app.bot.my_bookings.handlers import (cancel_logic, on_room_selected, on_list_last_bookings, on_list_all_bookings,
                                     on_list_last_bookings)
from app.bot.my_bookings.state import MyBookingState

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
        state=MyBookingState.room
    )

def get_confirmed_old_user_window():
    """Окно выбора перида списка бронирований."""
    return Window(
        Const("Возможно предоставление списка бронирований\n" \
              "за выбранный год или за текущий период."),
        Group(
            Button(Const("За текущий период"), id="confirm1", on_click=on_list_last_bookings),
            Button(Const("За весь год"), id="confirm2", on_click=on_list_all_bookings),
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
        ),
        state=MyBookingState.all_or_last
    )

def get_year_window() -> Window:
    """Окно ввода года.""" 
    Window(
        Const("Введите год, за который нужно вывести бронирования."),
        MessageInput(on_list_last_bookings),
        Group(
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        state=MyBookingState.year
)

def get_bookings_window() -> Window:
    """Окно вывода информации о каждом бронировании с кнопками в каждом бронировании.""" 
    Window(
        Format({text_book}),
        Group(
            Button(Const("Внести платеж"), id="pay", on_click=on_add_pay),
            Button(Const("Удалить запись"), id="delete", on_click=on_delete),
            Back(Const("Назад")),
            Cancel(Const("Отмена"), on_click=cancel_logic),
            width=2
        ),
        getter=get_all_last_bookings,
        state=MyBookingState.last
)