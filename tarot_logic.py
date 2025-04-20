from read_taro import data, get_random_cards, get_spread_text
from ai_interpreter import get_ai_interpretation

def get_tarot_response(spread_type):
    cards = get_random_cards(data, count=3 if spread_type != "yes_no" else 1)
    text = get_spread_text(data, spread_type, cards)
    ai_text = get_ai_interpretation(spread_type, cards)
    return text + "\n\n✨ Интерпретация от таролога:\n" + ai_text
