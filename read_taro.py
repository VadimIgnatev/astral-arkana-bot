import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random

# ==== Подключение к Google Таблице ====
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

spreadsheet = client.open("TaroBot_Cards")
sheet = spreadsheet.sheet1
data = sheet.get_all_records()

# ==== Вспомогательная функция: случайные карты ====
def get_random_cards(data, count=3):
    grouped = {}
    for card in data:
        grouped.setdefault(card['Аркан'], []).append(card)

    selected_names = random.sample(list(grouped.keys()), count)
    selected_cards = [random.choice(grouped[name]) for name in selected_names]
    return selected_cards

# ==== ГЛАВНАЯ ФУНКЦИЯ: Форматированный расклад ====
def get_spread_text(data, spread_type="classic", cards=None):
    spreads = {
        "classic": {
            "name": "🔮 Расклад: Прошлое — Настоящее — Будущее",
            "count": 3,
            "positions": ["Прошлое", "Настоящее", "Будущее"]
        },
        "yes_no": {
            "name": "⚖️ Ответ Да / Нет",
            "count": 1,
            "positions": ["Ответ"]
        },
        "love": {
            "name": "❤️ Расклад на отношения",
            "count": 3,
            "positions": ["Вы", "Партнёр", "Потенциал"]
        },
        "money": {
            "name": "💰 Расклад на финансы",
            "count": 3,
            "positions": ["Финансовое прошлое", "Настоящее", "Будущее"]
        },
        "day": {
            "name": "☀️ Расклад дня",
            "count": 3,
            "positions": ["Совет дня", "Возможность", "Опасность"]
        }
    }

    spread = spreads[spread_type]
    if cards is None:
        cards = get_random_cards(data, spread["count"])

    result = [f"*{spread['name']}*"]
    for pos, card in zip(spread["positions"], cards):
        result.append(f"\n*{pos}:* _{card['Аркан']} ({card['Положение']})_")
        result.append(f"_Смысл:_ {card['Общий смысл']}")
        result.append(f"_Совет:_ {card['Совет']}")

    return "\n".join(result)

# ==== Использование: расклад и AI-интерпретация ====
if __name__ == "__main__":
    from ai_interpreter import get_ai_interpretation

    # Получаем расклад на отношения (один и тот же набор карт для текста и AI)
    cards = get_random_cards(data, 3)
    text = get_spread_text(data, "love", cards)
    ai_text = get_ai_interpretation("Расклад на отношения", cards)

    # Выводим результат
    print(text)
    print("\n✨ Интерпретация от таролога:")
    print(ai_text)
