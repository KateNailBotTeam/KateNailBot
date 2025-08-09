from aiogram.fsm.state import State, StatesGroup


class BroadcastMessage(StatesGroup):
    waiting_for_text = State()
