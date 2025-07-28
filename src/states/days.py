from aiogram.fsm.state import State, StatesGroup


class Days(StatesGroup):
    first_day = State()
    last_day = State()
    apply_changes = State()
