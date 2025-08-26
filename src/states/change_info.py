from aiogram.fsm.state import State, StatesGroup


class ChangeInfo(StatesGroup):
    get_text = State()
