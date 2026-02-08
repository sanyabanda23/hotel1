from aiogram.fsm.state import StatesGroup, State


class OutputBookingsState(StatesGroup):
    dialog_start = State()
    books = State()
    sum_pay = State()

class ClearState(StatesGroup):
    delete = State()

    