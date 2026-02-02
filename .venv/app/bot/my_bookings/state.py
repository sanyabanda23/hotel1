from aiogram.fsm.state import StatesGroup, State


class MyBookingState(StatesGroup):
    room = State()
    all_or_last = State()
    year = State()
    success = State()