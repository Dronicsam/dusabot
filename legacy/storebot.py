# Подключения
import logging
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage


from db import BotDB
from config import TOKEN
from registration import UserState


logging.basicConfig(level=logging.INFO)

BotDB = BotDB('../store.db')
dusaBot = Bot(token=TOKEN)
dp = Dispatcher(dusaBot, storage=MemoryStorage())

# Кнопки

inline_btn_1 = InlineKeyboardButton('Покупатель', callback_data='btn1')
inline_btn_2 = InlineKeyboardButton('Продавец', callback_data='btn2')
inline_btn_3 = InlineKeyboardButton('Да', callback_data='btn3')  # учетной записи нет
inline_btn_4 = InlineKeyboardButton('Нет', callback_data='btn4')  # учетной записи нет
inline_btn_5 = InlineKeyboardButton('Продолжить', callback_data='btn5')  # учетная запись есть
inline_btn_8 = InlineKeyboardButton('Пересоздать', callback_data='btn8')
inline_btn_6 = InlineKeyboardButton('Да', callback_data='btn6')  # Поменять размер
inline_btn_7 = InlineKeyboardButton('Нет', callback_data='btn7')  # Не менять размер
registrate_inline_btn = InlineKeyboardButton('Зарегистрироваться', callback_data='regbtn')
inline_kb1 = InlineKeyboardMarkup().row(inline_btn_1, inline_btn_2)
inline_kb2 = InlineKeyboardMarkup().row(inline_btn_3, inline_btn_4)
inline_kb3 = InlineKeyboardMarkup().row(inline_btn_5, inline_btn_8)
inline_kb4 = InlineKeyboardMarkup().row(inline_btn_6, inline_btn_7)
greet_kb = InlineKeyboardMarkup().add(registrate_inline_btn)


# Код


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    hellomessage = 'Здравствуйте! Этот бот поможет вам найти интересующую вас одежду!'
    await message.answer(hellomessage, reply_markup=greet_kb)


@dp.message_handler(commands=['delete'])
async def delete(message: types.Message):
    deletemsg = 'Запись успешено удалена'
    await message.answer(deletemsg)
    BotDB.cancel_choise(message.from_user.id)


@dp.callback_query_handler(lambda recreate: recreate.data == 'btn8')
async def recreate_btn(callback_query: types.CallbackQuery):
    BotDB.cancel_choise(callback_query.from_user.id)
    reg_message = 'Кем вы хотите быть?'
    await dusaBot.send_message(callback_query.from_user.id, reg_message, reply_markup=inline_kb1)


@dp.callback_query_handler(lambda s: s.data == 'regbtn')
async def registration(callback_query: types.CallbackQuery):
    reg_message = 'Кем вы хотите быть?'
    await dusaBot.send_message(callback_query.from_user.id, reg_message, reply_markup=inline_kb1)


@dp.message_handler(content_types='text')
async def size(message: types.Message):
    tg_id = message.from_user.id
    sizev = message.text
    status = BotDB.get_status(tg_id)
    try:
        sizev = int(sizev)
        if BotDB.check_size(tg_id):
            BotDB.choose_size(sizev, message.from_user.id)
            await message.answer('Размер успешно указан!')
            if status == 0:
                info = BotDB.get_info(tg_id)
                await message.answer('Теперь ваша анкета выглядит так:')
                await message.answer(info[0])
            else:
                pass
        else:
            await message.answer('Размер уже указан. Хотите поменять?', reply_markup=inline_kb4)
    except ValueError:
        await message.answer('Введите размер в виде числа')


@dp.callback_query_handler(lambda e: e.data == 'btn6')  # Кнопка да при смене размера
async def size_changing(callback_query: types.CallbackQuery):
    await dusaBot.send_message(callback_query.from_user.id, 'Выберите размер')
    tg_id = callback_query.from_user.id
    BotDB.delete_size(tg_id)


@dp.callback_query_handler(lambda p: p.data == 'btn7')  # Кнопка нет при смене размера
async def size_changing_cancel(callback_query: types.CallbackQuery):
    await dusaBot.send_message(callback_query.from_user.id, 'Выбор отменен')


@dp.callback_query_handler(lambda c: c.data == 'btn1')
async def process_callback_buyer(callback_query: types.CallbackQuery):
    try:
        tg_id = callback_query.from_user.id
        name = callback_query.from_user.first_name
        choose = 0
        nickname = callback_query.from_user.username
        link = 'https://t.me/' + nickname
        BotDB.add_user(tg_id, name, choose, link)
        await dusaBot.send_message(callback_query.from_user.id, f'Ваше имя: {name}. Ссылка на вас: {link}.\n'
                                                                f'Продолжить?', reply_markup=inline_kb2)
    except Exception as ex:
        print(ex)
        await dusaBot.send_message(callback_query.from_user.id, 'Учетная запись уже создана.',
                                   reply_markup=inline_kb3)


@dp.callback_query_handler(lambda f: f.data == 'btn2')
async def process_callback_seller(callback_query: types.CallbackQuery):
    try:
        tg_id = callback_query.from_user.id
        name = callback_query.from_user.first_name
        choose = 1
        nickname = callback_query.from_user.username
        link = 'https://t.me/' + nickname
        BotDB.add_user(tg_id, name, choose, link)
        await dusaBot.send_message(callback_query.from_user.id, f'Ваше имя: {name}. Ссылка на вас: {link}.\n'
                                                                f'Продолжить?', reply_markup=inline_kb2)
    except Exception as ex:
        print(ex)
        await dusaBot.send_message(callback_query.from_user.id, 'Учетная запись уже создана.',
                                   reply_markup=inline_kb3)


@dp.callback_query_handler(lambda g: g.data == 'btn5')
async def ancet_exist(callback_query: types.CallbackQuery):
    tg_id = callback_query.from_user.id
    status = BotDB.get_status(tg_id)
    info = BotDB.get_info(tg_id)
    photo_id = info[1]
    if status == 1:
        await dusaBot.send_message(callback_query.from_user.id, 'Ваша анкета выглядит так:')
        await dusaBot.send_photo(chat_id=callback_query.from_user.id, photo=photo_id)
        await dusaBot.send_message(callback_query.from_user.id, info[0])
    else:
        await dusaBot.send_message(callback_query.from_user.id, 'Ваша анкета выглядит так:')
        await dusaBot.send_message(callback_query.from_user.id, info[0])


@dp.callback_query_handler(lambda sizebtn: sizebtn.data == 'btn3')
async def size_cont(callback_query: types.CallbackQuery):
    tg_id = callback_query.from_user.id
    status = BotDB.get_status(tg_id)
    if status == 0:
        await dusaBot.send_message(callback_query.from_user.id, 'Выберите размер')
    else:
        await dusaBot.send_message(callback_query.from_user.id, 'Выберите размер, а затем пришлите фотографию')


@dp.callback_query_handler(lambda cancel: cancel.data == 'btn4')
async def cancel_reg(callback_query: types.CallbackQuery):
    tg_id = callback_query.from_user.id
    BotDB.cancel_choise(tg_id)
    await dusaBot.send_message(callback_query.from_user.id, 'Регистрация отменена')


@dp.message_handler(content_types=['photo'])
async def get_photo(message: types.Message):
    tg_id = message.from_user.id
    status = BotDB.get_status(tg_id)
    if status == 1:
        document_id = message.photo[0].file_id
        BotDB.get_photo(document_id, tg_id)
        await message.reply('Фотография сохранена')
        info = BotDB.get_info(tg_id)
        photo_id = info[1]
        await message.answer('Теперь ваша анкета выглядит так:')
        await dusaBot.send_photo(chat_id=message.chat.id, photo=photo_id)
        await message.answer(info[0])
    else:
        await dusaBot.send_message(message.chat.id, 'Вы не продавец!')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
