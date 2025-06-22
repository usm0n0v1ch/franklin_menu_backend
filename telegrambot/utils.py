# telegrambot/utils.py
import requests
from .telegram_config import TELEGRAM_TOKEN, CHAT_ID

def send_message(text, chat_id=CHAT_ID):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
    }
    return requests.post(url, data=payload)
