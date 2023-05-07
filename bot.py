import aiogram.utils.exceptions
import asyncio
import io
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram import types
from aiogram.types import BotCommand
import logging

from TT_Bot_Db_Manager import TT_Bot_Db_Manager
from HtmlTemplate import HtmlTemplate

logging.basicConfig(filename='app.log', level=logging.INFO)

# Такие данные лучше хранить в переменных окружения, для простоты прописал в коде
# Имя бота @TT_Test_12bot
TOKEN = "1111111:22222223333334444"

# Номер телефона пользователя, который сможет работать с ботом
allowed_phone_number = "380123456789"
db = TT_Bot_Db_Manager(host='127.0.0.1', user='root', password='1234', database='TT_Bot')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

AuthorizeUserId = 0
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(msg: types.Message):
    await msg.answer(f"Я бот. Приятно познакомиться,{msg.from_user.first_name}")

# Запрос на авторизацию от пользователя, если пользователь уже авторизован ничего не делаем
# Если нет, просим отправить номер телефона
@dp.message_handler(commands=['authorize'])
async def text_write_handler(msg: types.Message):
    if AuthorizeUserId == msg.from_user.id:
        await msg.answer("Вы уже авторизовались, можете написать текст для рассылки")
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
        keyboard.add(button_phone)
        await msg.answer("Отправь свой номер телефона, для авторизации", reply_markup=keyboard)

# Обработка получения контакта пользователя
# Если номер телефона пользователя валидный, мы запоминаем Id
@dp.message_handler(content_types=['contact'])
async def phone_send_handler(msg: types.Message):
    global AuthorizeUserId  
    if  msg.contact.phone_number == allowed_phone_number:
        AuthorizeUserId = msg.from_user.id
        await msg.answer("Аторизация прошла успешно, напишите текст для рассылки")
    else:
        await msg.answer("Ваш номер не удалось авторизировать")

# Получение текста для рассылки
@dp.message_handler(content_types=['text'])
async def get_text_messages(msg: types.Message):
    # Если текст от неавторизированного пользователя, уведомляем что нужно авторизироваться
    if AuthorizeUserId != msg.from_user.id:
        await msg.answer("Нужно авторизоваться.")
        return

    # если в таблице нет записей, уведомляем об этом
    records = db.get_records()
    if not records:
        await msg.answer('Список пользователей для рассылки пуст')
        return

    arr_str = []
    count_all = 0
    count_errors = 0

    await msg.answer('Начинаю отправку')
    # разбиваем пользователей на блоки по 100 штук
    for chunk in chunks(records, 100):
        results = await send_messages(chunk, msg)
        # групируем пользователей и статус отправки им сообщений
        for record, result in zip(chunk, results):
            # создаём строку для таблицы отчёта
            arr_str.append(HtmlTemplate.create_line_table(record['IdTgUser'], result))
            if result == "Не отправлено":
                count_errors += 1
            count_all += 1

    # создаём файл для отчета об рассылке сообщений
    file_bytes = io.BytesIO(HtmlTemplate.create_file(arr_str, msg.text, str(count_all), str(count_errors), str(count_all - count_errors)).encode())
    input_file = types.InputFile(file_bytes, "report.html")
    await bot.send_document(AuthorizeUserId, input_file)

async def send_messages(records, msg):
    tasks = [asyncio.create_task(send_message(record, msg)) for record in records]
    results = await asyncio.gather(*tasks)
    return results

async def send_message(record, msg):
    try:
        message = await bot.send_message(record['IdTgUser'], msg.text)
        print(f'Сообщение отправлено: {message.text}')
        return "Отправлено"
    except aiogram.utils.exceptions.ChatNotFound as e:
        print(f'Ошибка при отправке сообщения: {e}')
        logging.error(f'Ошибка при отправке сообщения: {e}')
        return "Не отправлено"

def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

# обработа файла для добавлений новых пользователей
@dp.message_handler(content_types=['document'])
async def handle_document(msg: types.Message):
    if AuthorizeUserId != msg.from_user.id:
        await msg.answer("Нужно авторизоваться.")
        return

    # проверяем чтобы разширений было нужно формата
    if msg.document.mime_type == "application/json":
        file_info = await bot.get_file(msg.document.file_id)
        file = await bot.download_file(file_info.file_path)

        result_message = db.add_records_from_json_file(file)
        await msg.answer(result_message)
    else:
        await msg.answer("Пожалуйста, отправьте файл с расширением .json")
    
async def on_startup(dp):
    await bot.set_my_commands(
    [
        BotCommand(command='/start', description='Начать работу'),
        BotCommand(command='/authorize', description='Проверить статус авторизации'),
    ])

if __name__ == '__main__':
   executor.start_polling(dp, on_startup=on_startup)





