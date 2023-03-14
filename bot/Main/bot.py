import os
from contextlib import suppress
from googlesearch import search
from atlassian import Confluence
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Text
from settings import file_id_bd, file_id_ad, token
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified
from functions import login_true, open_file, log, Password
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup




# Параметры подключения:
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Словари для хранения:
data_list = {}
user_data = {}
callback_numbers = CallbackData("fabnum", "action")

# Формы:
class Form(StatesGroup):
    id_dop = State() 
    name_dop = State()

# Стартовое меню
# Проверяем есть ли пользователь в БД, если нет, просим отправить номер телефона
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    if login_true(message.from_user.id, file_id_bd, file_id_ad) == True:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.row(types.KeyboardButton(text="Отправить", request_contact=True), types.KeyboardButton(text="⠀Отмeнa"))
        await bot.send_message(message.chat.id, "Для использования бота необходимо направить данные.", reply_markup=keyboard)
    else:
        pass

# Мониторим данные типа 'contact' и пересылаем их на наш аккаунт в ТГ:
@dp.message_handler(content_types=['contact'])
async def contact(message):
    if message.contact is not None:

        await bot.send_message(message.chat.id, 'Запрос успешно отправлен.', reply_markup=types.ReplyKeyboardRemove())
        global phonenumber
        open_file(file_id_ad, '\n' + str(message.from_user.id) + '_' + str(message.from_user.first_name) + '_' + str(message.contact.phone_number), 'a')

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.row(
                types.InlineKeyboardButton(text="Принять", callback_data="authorization_yes"),
                types.InlineKeyboardButton(text="Отклонить", callback_data="authorization_no"))
        markup.add(types.InlineKeyboardButton(text="Удалить сообщение", callback_data="delet"))

        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
        await bot.send_message(chat_id='yourtgid', text=('<b>Новый запрос на авторизацию:</b>\n\n' + 
                                                    'ID: ' + str(message.from_user.id) + '\n' + 
                                                    'Имя: ' + str(message.from_user.first_name) + '\n' + 
                                                    'Телефон: ' + str(message.contact.phone_number)), reply_markup=markup)

# Кнопка отмены:
@dp.message_handler(Text(equals='⠀Отмeнa', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
    await bot.send_message(message.chat.id, 'Запрос успешно отменен.', reply_markup=types.ReplyKeyboardRemove())

#Авторизация одобрение:
@dp.callback_query_handler(text="authorization_yes")
async def call_authorization_yes(callback: types.CallbackQuery):
    await callback.answer()
    open_file(file_id_bd,'\n' + str(callback.message.text.split('\n')[2]).replace("ID: ","") + '_' 
                        + str(callback.message.text.split('\n')[3]).replace("Имя: ","") + '_' 
                        + str(callback.message.text.split('\n')[4]).replace("Телефон: ",""), 'a')
    await bot.send_message(str(callback.message.text.split('\n')[2]).replace("ID: ",""), 'Введите ваш логин в формате: login-"Ваш логин"')

#Авторизация отклонить:
@dp.callback_query_handler(text="authorization_no")
async def call_authorization_no(callback: types.CallbackQuery):
    await callback.answer()
    await bot.send_message(str(callback.message.text.split('\n')[2]).replace("ID: ",""), 'Запрос отклонен.')

#Очистка сообщений:
@dp.callback_query_handler(text="delet")
async def call_delet(callback: types.CallbackQuery):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    await callback.answer()

#Поиск:
@dp.message_handler(content_types=["text"])
async def say_bot_handler(message: types.Message, state: FSMContext):
    if message.text == '/start': 
        pass
    elif message.text.split('-')[0] == 'login':
        open_file('\\Desktop\\bot\\Login\\Pass\\' + str(message.from_user.id) + 'log.txt', message.text.split('-')[-1], 'w')
        await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)    
        await bot.send_message(message.chat.id, 'Введите пароль в формате: Pass-"Ваш пароль"')
    elif message.text.split('-')[0] == 'Pass':
        open_file('\\Desktop\\bot\\Login\\Pass\\' + str(message.from_user.id) + 'Pass.txt', message.text.split('-')[-1], 'w')
        try:
            confluence = Confluence(url='yoururl', username=log(message.from_user.id), password=Password(message.from_user.id))
            cql = 'yourcql'
            confluence.cql(cql, start=0, limit=5, expand=None, include_archived_spaces=None, excerpt=None)
            await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)    
            await bot.send_message(message.chat.id, 'Авторизация прошла успешно.')
        except:
            await bot.send_message(message.chat.id, 'Неверный логин\пароль, повторите авторизацию.\nВведите ваш логин в формате: login-"Ваш логин"')     
    else:
        if login_true(message.from_user.id, file_id_bd, file_id_ad) == True:
            pass
        elif login_true(message.from_user.id, file_id_bd, file_id_ad) == False:
            pass
        else:
            try:
                confluence = Confluence(url='yoururl', username=log(message.from_user.id), password=Password(message.from_user.id))
                cql = 'yourcql "' + str(" ".join(message.text.split())) + '"'
                d = confluence.cql(cql, start=0, limit=5, expand=None, include_archived_spaces=None, excerpt=None)
                b = d['results']
                if b == []:
                    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    markup.add( types.InlineKeyboardButton(text="Удалить", callback_data="delet"))
                    await bot.send_message(message.chat.id, "На вики ничего не найдено\nЗапрос в гугл -" + 
                                                            str(list(search(str(message.text), lang="ru", num_results=1))[0]), reply_markup=markup)
                elif len(b) < 5:
                    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    for a in range(len(b)): markup.insert(types.InlineKeyboardButton(text=b[int(a)]['content']['title'], 
                                                                                     callback_data='page_' + str(b[int(a)]['content']['id'])))
                    markup.row( types.InlineKeyboardButton(text="ЗАКРЫТЬ", callback_data="delet"))
                    await bot.send_message(message.chat.id, 'Результат поиска:' + '"' + message.text + '"', reply_markup=markup)                
                else:
                    await bot.delete_message(chat_id=message.from_user.id, message_id=message.message_id)
                    markup = types.InlineKeyboardMarkup(row_width=1)
                    for a in range(len(b)): markup.insert(types.InlineKeyboardButton(text=b[int(a)]['content']['title'], 
                                                                                     callback_data='page_' + str(b[int(a)]['content']['id'])))
                    markup.row( types.InlineKeyboardButton(text="ЗАКРЫТЬ", callback_data="delet"), 
                                types.InlineKeyboardButton(text=">>>", callback_data=callback_numbers.new(action="incr")))
                    await bot.send_message(message.chat.id, 'Результат поиска:' + '"' + message.text + '"', reply_markup=markup)
            except:
                await bot.send_message(message.chat.id, 'Неверный логин\пароль, повторите авторизацию.\nВведите ваш логин в формате: login-"Ваш логин"') 

#Пагинация:
async def update_num_text_fab(message: types.Message, new_value: int, login: str, Pass: str):
    confluence = Confluence(url='yoururl', username=login, password=Pass)
    with suppress(MessageNotModified):
        limit = int(5 + new_value)
        if limit <= 0 or limit == 5 :
            cql = 'yourcql"' + str(" ".join(message.text.replace('"','').replace('Результат поиска:','').split())) + '"'
            d = confluence.cql(cql, start=0, limit=5, expand=None, include_archived_spaces=None, excerpt=None)
            b = d['results']
            markup = types.InlineKeyboardMarkup(row_width=1)
            for a in range(len(b)): markup.insert(types.InlineKeyboardButton(text=b[int(a)]['content']['title'], callback_data='page_' + str(b[int(a)]['content']['id'])))
            markup.row( types.InlineKeyboardButton(text="ЗАКРЫТЬ", callback_data="delet"), 
                        types.InlineKeyboardButton(text=">>>", callback_data=callback_numbers.new(action="incr")))
            await message.edit_text(message.text.replace('"','').replace('Результат поиска:',''), reply_markup=markup)         
        else:
            cql = 'yourcql"' + str(" ".join(message.text.replace('"','').replace('Результат поиска:','').split())) + '"'
            d = confluence.cql(cql, start=new_value, limit=limit, expand=None, include_archived_spaces=None, excerpt=None)
            b = d['results']
            if len(b) < 5:
                markup = types.InlineKeyboardMarkup(row_width=1)
                for a in range(len(b)): markup.insert(types.InlineKeyboardButton(text=b[int(a)]['content']['title'], callback_data='page_' + str(b[int(a)]['content']['id'])))
                markup.row(types.InlineKeyboardButton(text="<<<", callback_data=callback_numbers.new(action="decr")), 
                            types.InlineKeyboardButton(text="ЗАКРЫТЬ", callback_data="delet"))
                await message.edit_text(message.text.replace('"','').replace('Результат поиска:',''), reply_markup=markup)
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                for a in range(5): markup.insert(types.InlineKeyboardButton(text=b[int(a)]['content']['title'], callback_data='page_' + str(b[int(a)]['content']['id'])))
                markup.row(types.InlineKeyboardButton(text="<<<", callback_data=callback_numbers.new(action="decr")), 
                            types.InlineKeyboardButton(text="ЗАКРЫТЬ", callback_data="delet"), 
                            types.InlineKeyboardButton(text=">>>", callback_data=callback_numbers.new(action="incr")))
                await message.edit_text(message.text.replace('"','').replace('Результат поиска:',''), reply_markup=markup)

#Изменения значений пагинации:
@dp.callback_query_handler(callback_numbers.filter(action=["incr", "decr"]))
async def callbacks_num_change_fab(callback: types.CallbackQuery, callback_data: dict):
    login = log(callback.from_user.id)
    Pass = Password(callback.from_user.id)
    user_value = user_data.get(callback.from_user.id, 0)
    action = callback_data["action"]
    if action == "incr":
        user_data[callback.from_user.id] = int(user_value) + 5
        await update_num_text_fab(callback.message, int(user_value) + 5, login, Pass)
    elif action == "decr":
        user_data[callback.from_user.id] = int(user_value) - 5
        await update_num_text_fab(callback.message, int(user_value) - 5, login, Pass)
    await callback.answer()
 
# Отправка PDF:
@dp.callback_query_handler(Text(startswith="page_"))
async def inline_kb_pdf(callback: types.CallbackQuery):
    await bot.delete_message(chat_id=callback.from_user.id, message_id=callback.message.message_id)
    confluence = Confluence(url='yoururl', username=log(callback.from_user.id), password=Password(callback.from_user.id))
    data_list['page'] = str(callback.data.split('_')[-1])
    try:
        with open (str(callback.message.chat.id) + '.pdf', 'wb') as file:
            file.write(confluence.export_page(str(data_list['page'])))
            file.close()
        with open (str(callback.message.chat.id) + '.pdf', 'rb') as file:
            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(types.InlineKeyboardButton(text="Удалить сообщение", callback_data="delet"))
            await bot.send_document(callback.message.chat.id, file, reply_markup=markup)
            file.close()
            await callback.answer()
        os.remove(str(callback.message.chat.id) + '.pdf')
    except:
        await bot.send_message(callback.message.chat.id, 'Неверный логин\пароль, повторите авторизацию.\nВведите ваш логин в формате: login-"Ваш логин"')




if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)