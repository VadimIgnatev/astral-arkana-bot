# This script is designed to work in standard Python environments.
# It does not require `micropip`, which is specific to Pyodide or web-based sandboxes.

import asyncio
import logging
from datetime import datetime
import os
import json
from dotenv import load_dotenv

# Включаем логирование
logging.basicConfig(level=logging.INFO)

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart

# Загружаем переменные окружения из .env
load_dotenv()

# 🔐 Токен Telegram-бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# 🗝️ Подключение credentials.json через переменную окружения (перенесено сюда для совместимости)
CREDENTIALS_JSON = os.getenv("CREDENTIALS_JSON")
if CREDENTIALS_JSON:
    with open("credentials.json", "w") as f:
        f.write(CREDENTIALS_JSON)

# Импортируем только нужные функции и переменные из read_taro,
# чтобы избежать кругового импорта
from read_taro import get_random_cards, get_spread_text, data

# ✅ Инициализация бота
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN)

dp = Dispatcher()

# Храним последний тип расклада для каждого пользователя
user_last_spread = {}
user_last_text = {}

# Основное меню выбора расклада
def get_main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💞 Отношения", callback_data="spread:love")],
        [InlineKeyboardButton(text="☀️ День", callback_data="spread:day")],
        [InlineKeyboardButton(text="🎯 Да / Нет", callback_data="spread:yes_no")]
    ])
    return kb

# Кнопки под раскладом
def get_post_spread_buttons(text_to_share=None):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔁 Повторить расклад", callback_data="repeat")],
        [InlineKeyboardButton(text="↩️ Назад к выбору", callback_data="back")],
        [InlineKeyboardButton(text="📤 Поделиться раскладом", switch_inline_query=text_to_share or "")]
    ])

# Основная функция для генерации текста расклада
# Вызывается извне

def get_tarot_response(spread_type: str) -> str:
    cards = get_random_cards(spread_type)
    interpretation = get_spread_text(spread_type, cards)
    return interpretation

# Команда /help — инструкция
@dp.message(F.text == "/help")
async def help_command(message: Message):
    await message.answer(
        """✨ *Как пользоваться AstralArkanaBot:*

1. Нажми кнопку и выбери тип расклада — любовь, день или да/нет.
2. Бот покажет тебе карты и их значения.
3. Ты получишь волшебную интерпретацию от AI-таролога.
4. Используй кнопки под раскладом: повтор, назад или поделиться.

🔮 *Прислушайся к шёпоту карт — ответы уже рядом.*"""
    )

# Команда /about
@dp.message(F.text == "/about")
async def about_command(message: Message):
    await message.answer(
        "🧠 *AstralArkanaBot* — это AI-бот, созданный на слиянии эзотерики и технологий. Он читает карты Таро, интерпретирует их с помощью искусственного интеллекта и помогает заглянуть внутрь себя."
    )

# Команда /contact
@dp.message(F.text == "/contact")
async def contact_command(message: Message):
    await message.answer(
        "📩 Если хочешь задать вопрос или предложить идею — напиши автору: [@key_bot_studio](https://t.me/key_bot_studio)"
    )

# Обработка inline-кнопки Контакты
@dp.callback_query(F.data == "contact_info")
async def handle_contact_info(callback: CallbackQuery):
    await callback.message.answer(
        "📩 Если хочешь задать вопрос или предложить идею — напиши автору: [@key_bot_studio](https://t.me/key_bot_studio)"
    )

# Команда /start с приветствием по времени суток
@dp.message(CommandStart())
async def start(message: Message):
    logging.info(f"Пользователь {message.from_user.id} запустил /start")

    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "🌅 *Доброе утро в AstralArkanaBot!*"
    elif 12 <= hour < 18:
        greeting = "🌞 *Светлого дня в AstralArkanaBot!*"
    else:
        greeting = "🌙 *Вечер добрый, искатель тайн...*"

    await message.answer_photo(
        photo=types.FSInputFile("images/start_illustration.jpg"),
        caption=(
            f"{greeting} ✨\n\n"
            "🃏 *Карты знают больше, чем слова.*\n"
            "🤖 _Я — разум, рождённый из магии и кода._\n\n"
            "🔻 Выбери, с чего начнём:"
        ),
        reply_markup=get_main_menu()
    )

# Обработка выбора расклада по inline-кнопкам
@dp.callback_query(F.data.startswith("spread:"))
async def handle_spread_selection(callback: CallbackQuery):
    user_id = callback.from_user.id
    spread_type = callback.data.split(":"[1])
    user_last_spread[user_id] = spread_type

    logging.info(f"Пользователь {user_id} выбрал расклад: {spread_type}")

    loading = await callback.message.answer("🔮 Раскладываю карты... Подожди немного...")
    text = get_tarot_response(spread_type)
    user_last_text[user_id] = text

    await bot.edit_message_text(
        text=text,
        chat_id=loading.chat.id,
        message_id=loading.message_id,
        reply_markup=get_post_spread_buttons(text)
    )

# Обработка повторного расклада
@dp.callback_query(F.data == "repeat")
async def handle_repeat(callback: CallbackQuery):
    user_id = callback.from_user.id
    spread_type = user_last_spread.get(user_id)

    if not spread_type:
        await callback.answer("Сначала выбери тип расклада.", show_alert=True)
        return

    logging.info(f"Пользователь {user_id} повторяет расклад: {spread_type}")

    loading = await callback.message.answer("🔁 Ещё один расклад...")
    text = get_tarot_response(spread_type)
    user_last_text[user_id] = text

    await bot.edit_message_text(
        text=text,
        chat_id=loading.chat.id,
        message_id=loading.message_id,
        reply_markup=get_post_spread_buttons(text)
    )

# Обработка кнопки "Назад"
@dp.callback_query(F.data == "back")
async def handle_back(callback: CallbackQuery):
    logging.info(f"Пользователь {callback.from_user.id} вернулся к выбору")
    await callback.message.edit_reply_markup()
    await callback.message.answer(
        "🔻 Выбери новый тип расклада:",
        reply_markup=get_main_menu()
    )

# Обработка всех необработанных текстов
@dp.message()
async def fallback_handler(message: Message):
    await message.answer(
        "🔍 Я пока понимаю только команды и кнопки.\nПопробуй выбрать расклад или нажми /start 😊"
    )

# Запуск
async def main():
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🔮 Начать расклад"),
        types.BotCommand(command="help", description="ℹ️ Как пользоваться ботом"),
        types.BotCommand(command="about", description="🧠 О боте"),
        types.BotCommand(command="contact", description="📩 Контакты")
    ])
    logging.info("Запуск бота AstralArkanaBot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
