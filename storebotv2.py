# Подключения
import logging
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardRemove


from db import BotDB
from config import TOKEN
import messages
import buttons
from registration import UserState
from shoes_search import Sellers
from size import Size
from photo import Photo

logging.basicConfig(level=logging.INFO)

BotDB = BotDB('store.db')
dusaBot = Bot(token=TOKEN)
dp = Dispatcher(dusaBot, storage=MemoryStorage())

# Код


@dp.message_handler(commands=['start', 'reg'])
async def start(message: types.Message):
    await dusaBot.send_message(message.chat.id, messages.reg_msg, reply_markup=buttons.greet_kb)


@dp.message_handler(text='Отмена', state=UserState)
@dp.message_handler(state=UserState, commands='cancel')
async def cancel_handler(message: types.Message, state: FSMContext):

    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.answer(messages.cancel_reg)


@dp.message_handler(text='Зарегистрироваться')
@dp.callback_query_handler(lambda reg: reg.data == 'reg_btn')
async def user_register(callback_query: types.CallbackQuery):
    tg_id = callback_query.from_user.id
    check = BotDB.get_status(tg_id)
    if check is None:
        await dusaBot.send_message(callback_query.from_user.id, messages.name_msg)
        await UserState.name.set()
    else:
        await dusaBot.send_message(callback_query.from_user.id, messages.user_exist, reply_markup=buttons.rec_or_not_kb)


@dp.message_handler(text='Поменять анкету')
@dp.callback_query_handler(lambda recreate: recreate.data == 'rec_btn')
async def recreate_account(callback_query: types.CallbackQuery):
    tg_id = callback_query.from_user.id
    BotDB.cancel_match_buy(tg_id)
    BotDB.cancel_choise(tg_id)
    BotDB.cancel_photos(tg_id)
    await dusaBot.send_message(callback_query.from_user.id, messages.name_msg, reply_markup=ReplyKeyboardRemove())
    await UserState.name.set()


@dp.callback_query_handler(lambda recreate: recreate.data == 'drec_btn')
async def dont_recreate_account(callback_query: types.CallbackQuery):
    tg_id = callback_query.from_user.id
    status = BotDB.get_status(tg_id)
    info = BotDB.get_info(tg_id)
    if status == 'Продавец':
        await dusaBot.send_message(callback_query.from_user.id, messages.ancet_now)
        photos = BotDB.check_photo(tg_id)
        for i in range(len(photos)):
            await dusaBot.send_photo(callback_query.from_user.id, photo=photos[i])
        await dusaBot.send_message(callback_query.from_user.id, info, reply_markup=buttons.seller_menu_kb)
    else:
        await dusaBot.send_message(callback_query.from_user.id, messages.ancet_now)
        await dusaBot.send_message(callback_query.from_user.id, info, reply_markup=buttons.buyer_menu_kb)


@dp.message_handler(state=UserState.name)
async def get_username(message: types.Message, state: FSMContext):
    try:
        nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        temp_city = message.text
        for i in nums:
            if i in temp_city:
                raise Exception
        await state.update_data(name=message.text)
        await message.answer(messages.size_msg)
        await UserState.size.set()
    except Exception as ex:
        logging.info('Nums in name %r', ex)
        await message.answer('Введите имя без чисел')
        return


@dp.message_handler(state=UserState.size)
async def get_size(message: types.Message, state: FSMContext):
    try:
        temp_size = int(message.text)
        await state.update_data(size=temp_size)
    except ValueError as ex:
        logging.info('Letters in size %r', ex)
        await message.answer("Введите размер в виде числа")
        return
    await message.answer(messages.city_msg)
    await UserState.city.set()


@dp.message_handler(state=UserState.city)
async def get_city(message: types.Message, state: FSMContext):
    try:
        nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        temp_city = message.text
        for i in nums:
            if i in temp_city:
                raise Exception
        await state.update_data(city=message.text)
        await message.answer(messages.type_of_buy_msg, reply_markup=buttons.tob_kb)
        await UserState.type_of_buy.set()
    except Exception as ex:
        logging.info('Nums in сity %r', ex)
        await message.answer('Введите город без чисел')
        return


@dp.callback_query_handler(lambda tob_irl: tob_irl.data == 'irl_btn', state=UserState.type_of_buy)
async def get_tob(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(type_of_buy='Самовывоз')
    await dusaBot.send_message(callback_query.from_user.id, messages.choise_msg, reply_markup=buttons.choise_kb)
    await UserState.choise.set()


@dp.callback_query_handler(lambda tob_irl: tob_irl.data == 'delivery_btn', state=UserState.type_of_buy)
async def get_tob(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(type_of_buy='Доставка')
    await dusaBot.send_message(callback_query.from_user.id, messages.choise_msg, reply_markup=buttons.choise_kb)
    await UserState.choise.set()


@dp.callback_query_handler(lambda tob_irl: tob_irl.data == 'dmater_btn', state=UserState.type_of_buy)
async def get_tob(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(type_of_buy='Доставка или самовывоз')
    await dusaBot.send_message(callback_query.from_user.id, messages.choise_msg, reply_markup=buttons.choise_kb)
    await UserState.choise.set()


@dp.callback_query_handler(lambda seller: seller.data == 'seller_btn', state=UserState.choise)
async def get_sell(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(choise='Продавец')
    await dusaBot.send_message(callback_query.from_user.id, messages.name_of_shoes)
    await UserState.namesh.set()


@dp.callback_query_handler(lambda buyer: buyer.data == 'buyer_btn', state=UserState.choise)
async def get_buy(callback_query: types.CallbackQuery, state: FSMContext):
    await state.update_data(choise='Покупатель')
    await dusaBot.send_message(callback_query.from_user.id, messages.reg_end)
    tg_id = callback_query.from_user.id
    nickname = callback_query.from_user.username
    if nickname is None:
        link = 'ссылка скрыта'
    else:
        link = 'https://t.me/' + nickname
    data = await state.get_data()
    BotDB.add_user(tg_id, data['name'], data['size'], data['choise'], link, data['city'])
    tob = data['type_of_buy']
    BotDB.get_tob(tob, tg_id)
    await dusaBot.send_message(callback_query.from_user.id, messages.ancet_now)
    info = BotDB.get_info(tg_id)
    await dusaBot.send_message(callback_query.from_user.id, info, reply_markup=buttons.buyer_menu_kb)
    if link == 'ссылка скрыта':
        await dusaBot.send_message(callback_query.from_user.id, messages.hidden_link)

    await state.finish()


@dp.message_handler(content_types=['text'], state=UserState.namesh)
async def get_namesh(message: types.Message, state: FSMContext):
    await state.update_data(namesh=message.text)
    await dusaBot.send_message(message.from_user.id, messages.photo_msg)
    await UserState.photo.set()


@dp.message_handler(content_types=['photo'], state=UserState.photo)
async def get_photo(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    num_of_photo = BotDB.number_photo(tg_id)
    if num_of_photo < 5:
        document_id = message.photo[0].file_id
        await state.update_data(photo=document_id)
        BotDB.get_photo(document_id, tg_id)
        await dusaBot.send_message(message.from_user.id, 'Фото принято', reply_markup=buttons.done_kb)
    else:
        await dusaBot.send_message(message.from_user.id, 'Превышено колличество фото')
        pass


@dp.message_handler(text='Готово', state=UserState.photo)
async def done(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    photos = BotDB.check_photo(tg_id)
    nickname = message.from_user.username
    if nickname is None:
        link = 'ссылка скрыта'
    else:
        link = 'https://t.me/' + nickname
    data = await state.get_data()
    BotDB.add_user(tg_id, data['name'], data['size'], data['choise'], link, data['city'])
    namesh = data['namesh']
    BotDB.get_namesh(namesh, tg_id)
    tob = data['type_of_buy']
    BotDB.get_tob(tob, tg_id)
    await message.answer(messages.reg_end)
    await message.answer(messages.ancet_now)
    for i in range(len(photos)):
        await dusaBot.send_photo(message.from_user.id, photo=photos[i])
    info = BotDB.get_info(tg_id)
    await dusaBot.send_message(message.from_user.id, info, reply_markup=buttons.seller_menu_kb)
    if link == 'ссылка скрыта':
        await dusaBot.send_message(message.from_user.id, messages.hidden_link)

    await state.finish()


@dp.message_handler(content_types=['any'], state=UserState.photo)
async def text_error(message: types.Message):
    await message.answer('Отправьте фотографию в правильном формате')


@dp.message_handler(commands=['delete'])
async def delete(message: types.Message):
    await message.answer(messages.deletemsg, reply_markup=buttons.reg_btn_kb)
    tg_id = message.from_user.id
    BotDB.cancel_match_buy(tg_id)
    BotDB.cancel_choise(tg_id)
    BotDB.cancel_photos(tg_id)


@dp.message_handler(text='Изменить размер обуви')
@dp.message_handler(commands='size')
async def change_size(message: types.Message):
    await message.answer('Введите нужный размер', reply_markup=buttons.cancel_kb)
    await Size.size.set()


@dp.message_handler(state=Size, text='Отмена')
@dp.message_handler(state=Size, commands='cancel')
async def cancel_size(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    status = BotDB.get_status(message.from_user.id)
    if status == 'Продавец':
        await message.answer(messages.size_cancel, reply_markup=buttons.seller_menu_kb)
    else:
        await message.answer(messages.size_cancel, reply_markup=buttons.buyer_menu_kb)


@dp.message_handler(content_types=['text'], state=Size.size)
async def choose_size(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    status = BotDB.get_status(tg_id)
    try:
        temp_size = int(message.text)
        await state.update_data(size=temp_size)
        data = await state.get_data()
        size = data['size']
        BotDB.select_size(size, tg_id)
        BotDB.cancel_match_buy(tg_id)
        if status == 'Продавец':
            await message.answer('Размер успешно изменен', reply_markup=buttons.seller_menu_kb)
        else:
            await message.answer('Размер успешно изменен', reply_markup=buttons.buyer_menu_kb)

        await state.finish()
    except ValueError:
        await message.answer("Введите размер в виде числа")
        return


@dp.message_handler(state=Sellers, text='Стоп')
@dp.message_handler(state=Sellers, commands='cancel')
async def cancel_search(message: types.Message, state: FSMContext):
    status = BotDB.get_status(message.from_user.id)
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    if status == 'Продавец':
        await message.answer(messages.search_cancel, reply_markup=buttons.seller_menu_kb)
    else:
        await message.answer(messages.search_cancel, reply_markup=buttons.buyer_menu_kb)


@dp.message_handler(text='Поиск')
@dp.message_handler(commands=['search', 's'])
async def start_search(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    status = BotDB.get_status(tg_id)
    if status == 'Покупатель' or status == 'Продавец':
        await state.update_data(buyer=tg_id)
        await message.answer(messages.ancet_now, reply_markup=ReplyKeyboardRemove())
        await dusaBot.send_message(message.chat.id, BotDB.get_info(tg_id), reply_markup=buttons.search_kb)
        await Sellers.seller.set()
    else:
        pass


@dp.callback_query_handler(lambda cs: cs.data == 'cancel_search', state=Sellers)
async def cancel_search_button(callback_query: types.CallbackQuery, state: FSMContext):
    status = BotDB.get_status(callback_query.from_user.id)
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    if status == 'Продавец':
        await dusaBot.send_message(callback_query.from_user.id, messages.search_cancel,
                                   reply_markup=buttons.seller_menu_kb)
    else:
        await dusaBot.send_message(callback_query.from_user.id, messages.search_cancel,
                                   reply_markup=buttons.buyer_menu_kb)


@dp.callback_query_handler(lambda ssearch: ssearch.data == 'start_search', state=Sellers.seller)
async def show_sellers(callback_query: types.CallbackQuery, state: FSMContext):
    tg_id = callback_query.from_user.id
    size = BotDB.get_size(tg_id)
    sellers = BotDB.count_sellers(size)
    await state.update_data(sellers=sellers)
    number_of_sellers = len(sellers) - 1
    if number_of_sellers >= 0:
        seller_id = sellers[number_of_sellers]
        if tg_id != seller_id:
            await state.update_data(seller=seller_id)
            photos = BotDB.check_photo(seller_id)
            for i in range(len(photos)):
                await dusaBot.send_photo(callback_query.from_user.id, photo=photos[i], reply_markup=buttons.stop_btn_kb)
            await dusaBot.send_message(callback_query.from_user.id, BotDB.get_info_global(seller_id),
                                       reply_markup=buttons.rate_kb)
            await state.update_data(number_of_sellers=number_of_sellers)
            await state.update_data(seller_to_add=seller_id)
        else:
            number_of_sellers -= 1
            if number_of_sellers >= 0:
                seller_id = sellers[number_of_sellers]
                photos = BotDB.check_photo(seller_id)
                for i in range(len(photos)):
                    await dusaBot.send_photo(callback_query.from_user.id, photo=photos[i])
                await dusaBot.send_message(callback_query.from_user.id, BotDB.get_info_global(seller_id),
                                           reply_markup=buttons.rate_kb)
                await state.update_data(number_of_sellers=number_of_sellers)
                await state.update_data(seller=seller_id)
                await state.update_data(seller_to_add=seller_id)
            else:
                status = BotDB.get_status(callback_query.from_user.id)
                if status == 'Продавец':

                    await dusaBot.send_message(callback_query.from_user.id, 'Анкет нет',
                                               reply_markup=buttons.seller_menu_kb)
                else:
                    await dusaBot.send_message(callback_query.from_user.id, 'Анкет нет',
                                               reply_markup=buttons.buyer_menu_kb)
                await state.finish()
    else:
        status = BotDB.get_status(callback_query.from_user.id)
        if status == 'Продавец':

            await dusaBot.send_message(callback_query.from_user.id, 'Анкет нет',
                                       reply_markup=buttons.seller_menu_kb)
        else:
            await dusaBot.send_message(callback_query.from_user.id, 'Анкет нет',
                                       reply_markup=buttons.buyer_menu_kb)
        await state.finish()


@dp.callback_query_handler(lambda like: like.data == 'plus_btn', state=Sellers)
async def like_ancet(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    buyer_id = data['buyer']
    sellers = data['sellers']
    number_of_sellers = data['number_of_sellers'] - 1
    seller_id = sellers[number_of_sellers]
    seller_to_add = data['seller_to_add']
    ids_check = BotDB.check_match_buy(buyer_id, seller_to_add)
    link = BotDB.get_link(seller_to_add)
    if ids_check is False:
        BotDB.add_match(seller_to_add, buyer_id)
        await dusaBot.send_message(seller_to_add, 'Ваше объявление понравилось пользователю!')
        await dusaBot.send_message(seller_to_add, BotDB.get_info(buyer_id))
        await dusaBot.send_message(buyer_id, 'Написать: ' + link)
    elif ids_check is True:
        await dusaBot.send_message(buyer_id, 'Вы уже реагировали на это объявление')
    if number_of_sellers >= 0:
        if buyer_id != seller_id:
            await state.update_data(seller=seller_id)
            photos = BotDB.check_photo(seller_id)
            for i in range(len(photos)):
                await dusaBot.send_photo(callback_query.from_user.id, photo=photos[i])
            await dusaBot.send_message(callback_query.from_user.id, BotDB.get_info_global(seller_id),
                                       reply_markup=buttons.rate_kb)
            await state.update_data(number_of_sellers=number_of_sellers)
            await state.update_data(seller_to_add=seller_id)
        else:
            number_of_sellers -= 1
            if number_of_sellers >= 0:
                await state.update_data(number_of_sellers=number_of_sellers)
                seller_id = sellers[number_of_sellers]
                await state.update_data(seller=seller_id)
                photos = BotDB.check_photo(seller_id)
                for i in range(len(photos)):
                    await dusaBot.send_photo(callback_query.from_user.id, photo=photos[i])
                await dusaBot.send_message(callback_query.from_user.id, BotDB.get_info_global(seller_id),
                                           reply_markup=buttons.rate_kb)
                await state.update_data(number_of_sellers=number_of_sellers)
                await state.update_data(seller_to_add=seller_id)
            else:
                status = BotDB.get_status(buyer_id)
                if status == 'Продавец':
                    await dusaBot.send_message(buyer_id, 'Анкеты кончились',
                                               reply_markup=buttons.seller_menu_kb)
                else:
                    await dusaBot.send_message(buyer_id, 'Анкеты кончились',
                                               reply_markup=buttons.buyer_menu_kb)
                await state.finish()

    elif number_of_sellers < 0:
        status = BotDB.get_status(buyer_id)
        if status == 'Продавец':
            await dusaBot.send_message(buyer_id, 'Анкеты кончились',
                                       reply_markup=buttons.seller_menu_kb)
        else:
            await dusaBot.send_message(buyer_id, 'Анкеты кончились',
                                       reply_markup=buttons.buyer_menu_kb)
        await state.finish()


@dp.callback_query_handler(lambda dislike: dislike.data == 'minus_btn', state=Sellers)
async def dislike_ancet(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    buyer_id = data['buyer']
    sellers = data['sellers']
    number_of_sellers = data['number_of_sellers'] - 1
    seller_id = sellers[number_of_sellers]
    if number_of_sellers > 0:
        if buyer_id != seller_id:
            await state.update_data(seller=seller_id)
            photos = BotDB.check_photo(seller_id)
            for i in range(len(photos)):
                await dusaBot.send_photo(callback_query.from_user.id, photo=photos[i])
            await dusaBot.send_message(callback_query.from_user.id, BotDB.get_info_global(seller_id),
                                       reply_markup=buttons.rate_kb)
            await state.update_data(number_of_sellers=number_of_sellers)
        else:
            if number_of_sellers < 0:
                status = BotDB.get_status(buyer_id)
                if status == 'Продавец':
                    await dusaBot.send_message(buyer_id, 'Анкеты кончились',
                                               reply_markup=buttons.seller_menu_kb)
                else:
                    await dusaBot.send_message(buyer_id, 'Анкеты кончились',
                                               reply_markup=buttons.buyer_menu_kb)
                await state.finish()
            else:
                await state.update_data(seller=seller_id)
                number_of_sellers -= 1
                await state.update_data(number_of_sellers=number_of_sellers)
                seller_id = sellers[number_of_sellers]
                photos = BotDB.check_photo(seller_id)
                for i in range(len(photos)):
                    await dusaBot.send_photo(callback_query.from_user.id, photo=photos[i])
                await dusaBot.send_message(callback_query.from_user.id, BotDB.get_info_global(seller_id),
                                           reply_markup=buttons.rate_kb)
                await state.update_data(number_of_sellers=number_of_sellers)

    elif number_of_sellers == 0 or number_of_sellers < 0:
        status = BotDB.get_status(buyer_id)
        if status == 'Продавец':
            await dusaBot.send_message(buyer_id, 'Анкеты кончились',
                                       reply_markup=buttons.seller_menu_kb)
        else:
            await dusaBot.send_message(buyer_id, 'Анкеты кончились',
                                       reply_markup=buttons.buyer_menu_kb)
        await state.finish()


@dp.message_handler(text='Изменить фото')
@dp.message_handler(commands=['photo'])
async def change_photo(message: types.Message):
    status = BotDB.get_status(message.from_user.id)
    if status == 'Продавец':
        await message.answer('Вы действительно хотите изменить фото?', reply_markup=buttons.confirm_kb)
    else:
        pass


@dp.callback_query_handler(lambda cancel: cancel.data == 'cancel_photo')
async def cancel_photo(callback_query: types.CallbackQuery):
    status = BotDB.get_status(callback_query.from_user.id)
    if status == 'Продавец':
        await dusaBot.send_message(callback_query.from_user.id,
                                   messages.photo_cancel, reply_markup=buttons.seller_menu_kb)
    else:
        await dusaBot.send_message(callback_query.from_user.id,
                                   messages.photo_cancel, reply_markup=buttons.buyer_menu_kb)


@dp.callback_query_handler(lambda confirm: confirm.data == 'confirm_photo')
async def photo_confirm(callback_query: types.CallbackQuery):
    await dusaBot.send_message(callback_query.from_user.id, 'Введите название вашей обуви',
                               reply_markup=ReplyKeyboardRemove())
    BotDB.cancel_photos(callback_query.from_user.id)
    await Photo.namesh.set()


@dp.message_handler(content_types='text', state=Photo.namesh)
async def get_namesh(message: types.Message, state: FSMContext):
    await state.update_data(namesh=message.text)
    await dusaBot.send_message(message.from_user.id, 'Отправьте фотографии вашей обуви до 5 штук')
    await Photo.photo.set()


@dp.message_handler(content_types='photo', state=Photo.photo)
async def photo(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    num_of_photo = BotDB.number_photo(tg_id)
    if num_of_photo < 5:
        document_id = message.photo[0].file_id
        await state.update_data(photo=document_id)
        BotDB.get_photo(document_id, tg_id)
        await dusaBot.send_message(message.from_user.id, 'Фото принято', reply_markup=buttons.done_kb)
    else:
        await dusaBot.send_message(message.from_user.id, 'Превышено колличество фото')
        pass


@dp.message_handler(text='Готово', state=Photo)
async def done_change(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id
    photos = BotDB.check_photo(tg_id)
    status = BotDB.get_status(tg_id)
    data = await state.get_data()
    namesh = data['namesh']
    BotDB.get_namesh(namesh, tg_id)
    BotDB.get_info(tg_id)
    await message.answer(messages.ancet_now)
    for i in range(len(photos)):
        await dusaBot.send_photo(message.from_user.id, photo=photos[i])
    info = BotDB.get_info(tg_id)
    if status == 'Продавец':
        await dusaBot.send_message(message.from_user.id, info, reply_markup=buttons.seller_menu_kb)
    else:
        await dusaBot.send_message(message.from_user.id, info, reply_markup=buttons.buyer_menu_kb)

    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=BotDB.close(), on_startup=BotDB.__init__('store.db'))
