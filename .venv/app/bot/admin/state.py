from aiogram.fsm.state import StatesGroup, State


class OutputBookingsState(StatesGroup):
    dialog_start = State()
    books = State()
    sum_pay = State()

class ClearState(StatesGroup):
    delete = State()

class FindUserState(StatesGroup):
    input_info = State()
    select_user = State()
    update_phone = State()
    update_name = State()
    update_description = State()
    update_vk = State()
    update_tg = State()

class CheckUserState(StatesGroup):
    phone_nom = State()
    