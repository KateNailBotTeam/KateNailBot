from aiogram.fsm.state import State, StatesGroup


class ChooseVisitDatetime(StatesGroup):
    waiting_for_date = State()
    waiting_for_time = State()
