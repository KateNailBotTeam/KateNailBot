from aiogram.fsm.state import State, StatesGroup


class CancelBooking(StatesGroup):
    waiting_for_choose_datetime = State()
    waiting_for_cancel_datetime = State()
