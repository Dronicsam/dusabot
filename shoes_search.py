from aiogram.dispatcher.filters.state import StatesGroup, State


class Sellers(StatesGroup):
    seller = State()
    buyer = State()
    number_of_sellers = State()
    sellers = State()
    seller_to_add = State()
