from aiogram.fsm.state import State, StatesGroup


class WorkingTimeStates(StatesGroup):
    waiting_for_time_range = State()
