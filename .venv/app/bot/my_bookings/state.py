from aiogram.fsm.state import StatesGroup, State


class MyBookingState(StatesGroup):
    room = State()
    all_or_last = State()
    last = State()
    input_cost = State()
    year = State()
    all_in_year = State()
    success = State()