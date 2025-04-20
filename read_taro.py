import random
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
from dotenv import load_dotenv

# Загружаем переменные из .env (для локальной разработки)
load_dotenv()

# Загружаем JSON из переменной окружения
CREDENTIALS_JSON = os.getenv("CREDENTIALS_JSON")
if CREDENTIALS_JSON:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        json.loads(CREDENTIALS_JSON),
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "credentials.json",
        ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    )

client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).sheet1

# Загружаем все данные из Google Sheet
data = sheet.get_all_records()

# Выбор случайных карт для раскладов
def get_random_cards(spread_type):
    if spread_type == "love":
        return random.sample(data, 3)
    elif spread_type == "day":
        return random.sample(data, 1)
    elif spread_type == "yes_no":
        return random.sample(data, 1)
    return []

# Текстовое представление расклада
def get_spread_text(spread_type, cards):
    if spread_type == "love" and len(cards) == 3:
        return (
            f"💞 *Любовный расклад:*\n\n"
            f"1. {cards[0]['Название']} — {cards[0]['Описание']}\n"
            f"2. {cards[1]['Название']} — {cards[1]['Описание']}\n"
            f"3. {cards[2]['Название']} — {cards[2]['Описание']}\n"
        )
    elif spread_type == "day" and len(cards) == 1:
        return f"☀️ *Карта дня:* {cards[0]['Название']}\n{cards[0]['Описание']}"
    elif spread_type == "yes_no" and len(cards) == 1:
        return f"🎯 *Ответ:* {cards[0]['Название']}\n{cards[0]['Описание']}"
    else:
        return "Ошибка при получении карт."
