from aiogram.fsm.state import State, StatesGroup


class DaysOff(StatesGroup):
    first_day_off = State()
    last_day_off = State()
