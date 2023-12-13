from aiogram.dispatcher.filters.state import StatesGroup, State


class Photo(StatesGroup):
    photo = State()
    namesh = State()