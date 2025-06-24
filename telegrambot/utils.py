import requests
from .models import WaiterCall
from .telegram_config import TELEGRAM_TOKEN, CHAT_ID
from django.utils import timezone


def send_waiter_request(table_id):
    """Отправляет запрос официанту с одной кнопкой 'Уже иду'"""
    called_time = timezone.now().strftime("%H:%M")
    text = f"""
🛎 Вызов официанта
Столик: #{table_id}
Время вызова: {called_time}
Статус: Ожидает подтверждения
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'reply_markup': {
            'inline_keyboard': [
                [{'text': '🟢 Уже иду', 'callback_data': f'coming_{table_id}'}]
            ]
        }
    }

    response = requests.post(url, json=payload)
    if response.json().get('ok'):
        return WaiterCall.objects.create(
            table_id=table_id,
            message_id=response.json()['result']['message_id']
        )
    return None


def update_waiter_status(table_id, status, message_id=None):
    """Обновляет статус и время в сообщении"""
    call = WaiterCall.objects.filter(
        table_id=table_id,
        message_id=message_id
    ).first()

    if not call:
        return False

    call.status = status
    call.save()

    # Формируем текст сообщения с временем
    called_time = call.called_at.strftime("%H:%M")
    coming_time = call.coming_at.strftime("%H:%M") if call.coming_at else "--:--"

    status_texts = {
        'coming': f"""
✅ Официант в пути
Столик: #{table_id}
Вызов: {called_time}
Принят в: {coming_time}
        """,
        'arrived': f"""
🎉 Официант на месте
Столик: #{table_id}
Вызов: {called_time}
Принят в: {coming_time}
Подошел в: {timezone.now().strftime("%H:%M")}
        """
    }

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/editMessageText"
    payload = {
        'chat_id': CHAT_ID,
        'message_id': message_id,
        'text': status_texts.get(status, f"🛎 Столик #{table_id} (вызов в {called_time})"),
        'parse_mode': 'HTML',
    }

    response = requests.post(url, json=payload)
    return response.json().get('ok', False)