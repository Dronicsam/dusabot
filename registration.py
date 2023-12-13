from aiogram.dispatcher.filters.state import StatesGroup, State


class UserState(StatesGroup):
    name = State()
    size = State()
    city = State()
    type_of_buy = State()
    choise = State()
    photo = State()
    number_of_photo = State()
    namesh = State()
