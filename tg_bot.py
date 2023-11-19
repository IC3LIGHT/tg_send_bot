import sqlite3
import logging
import aiogram
from aiogram import types
from aiogram import Bot, Dispatcher
from aiogram.dispatcher import filters
import subprocess


bot = Bot(token='6703848840:AAFXHzN6e7sRG5m7xytiglGaVOsWjeM4mTw')
logging.basicConfig(level=logging.INFO)
dp = Dispatcher(bot)

def add_table():
    conn = sqlite3.connect('mail.db')
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS mail_table (email TEXT, number INTEGER)")
    conn.commit()
    conn.close()

add_table()

def send_info(*values):
    conn = sqlite3.connect('mail.db')
    c = conn.cursor()
    for i in range(0, len(values), 2):
        value1 = values[i]
        value2 = values[i+1]
        c.execute("INSERT INTO mail_table VALUES (?, ?)", (value1, value2))
    conn.commit()
    conn.close()


@dp.message_handler(filters.Command(commands=['info']))
async def send_info_handler(message: types.Message):
    values = message.text.split()[1:]
    if len(values) % 2 == 0:
        send_info(*values)
        await message.answer('Почта передана')
        button = types.InlineKeyboardButton(text='Отправить', callback_data='send')
        keyboard = types.InlineKeyboardMarkup().add(button)
        await message.answer('Нажмите кнопку для отправки', reply_markup=keyboard)
    else:
        await message.answer('Перепроверьте значения')


@dp.callback_query_handler(text='send')
async def send_script_handler(callback_query: types.CallbackQuery):
    try:
        subprocess.run(["python", "mail_send.py"])
        await callback_query.message.answer('Скрипт успешно запущен')
        button_clear = types.InlineKeyboardButton(text='Очистить таблицу', callback_data='clear')
        keyboard = types.InlineKeyboardMarkup().add(button_clear)
        await callback_query.message.answer('Нажмите кнопку для очистки таблицы', reply_markup=keyboard)
    except Exception as e:
        await callback_query.message.answer(f'Ошибка при запуске скрипта: {e}')


@dp.callback_query_handler(text='clear')
async def clear_table_handler(callback_query: types.CallbackQuery):
    try:
        clear_table()
        await callback_query.message.answer('Таблица успешно очищена')
    except Exception as e:
        await callback_query.message.answer(f'Ошибка при очистке таблицы: {e}')

def clear_table():
    conn = sqlite3.connect('mail.db')
    c = conn.cursor()
    c.execute(f"DELETE FROM 'mail_table'")
    conn.commit()
    conn.close()

@dp.message_handler(commands=['clear_table'])
async def add_name(message: types.Message):
    clear_table()
    await message.reply((f"Таблица очищена"))






if __name__ == '__main__':
    aiogram.executor.start_polling(dp)
