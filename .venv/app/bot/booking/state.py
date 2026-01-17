from aiogram.fsm.state import StatesGroup, State


class BookingState(StatesGroup):
    phone_nom = State()
    check_nom = State()
    name = State()
    description_user = State()
    check_user = State()
    room = State()
    booking_date_start = State()
    booking_date_end = State()
    cost = State()
    confirmation = State()
    success = State()