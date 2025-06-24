import os
import sys
import logging
import asyncio
import httpx
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
)

# Django настройки
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'franklin_api.settings')

import django
django.setup()

from franklin_api.settings import TELEGRAM_BOT_TOKENS, ALLOWED_TELEGRAM_USERNAMES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = TELEGRAM_BOT_TOKENS['waiter']
API_BASE_URL = 'http://127.0.0.1:8000/api/telegram'

already_notified_ids = set()
authorized_chat_ids = set()

# /start команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.effective_user.username
    chat_id = update.effective_chat.id

    if username in ALLOWED_TELEGRAM_USERNAMES:
        authorized_chat_ids.add(chat_id)
        await update.message.reply_text("✅ Доступ официанту разрешён. Бот работает 👋")
        logger.info(f"Официант @{username} авторизован.")
    else:
        await update.message.reply_text("❌ У вас нет доступа к этому боту.")
        logger.warning(f"Попытка от неавторизованного пользователя @{username}")

# Получение новых заказов
async def check_new_orders(context: ContextTypes.DEFAULT_TYPE):
    if not authorized_chat_ids:
        return

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/new_orders/?role=waiter")
            response.raise_for_status()
            items = response.json()

            for item in items:
                if item['id'] not in already_notified_ids:
                    table = item['order']['table']
                    product = item['product']['name']
                    quantity = item.get('quantity', 1)
                    options = item.get('options', [])
                    created_at = item.get("created_at")

                    created_at_str = (
                        datetime.fromisoformat(created_at).strftime("%Y-%m-%d %H:%M")
                        if created_at else "неизвестно"
                    )
                    options_text = "\n".join([f"{opt['type']}: {opt['name']}" for opt in options]) or "—"

                    msg = (
                        f"🍹 <b>Новый заказ</b>\n"
                        f"🍽️ <b>Столик:</b> {table}\n"
                        f"🧃 <b>Продукт:</b> {product} (x{quantity})\n"
                        f"⚙️ <b>Опции:</b>\n{options_text}\n"
                        f"🕒 <b>Время заказа:</b> {created_at_str}\n"
                        f"⏳ <b>Статус:</b> Новый"
                    )

                    keyboard = InlineKeyboardMarkup([[
                        InlineKeyboardButton("✅ Готово", callback_data=f"done_{item['id']}")
                    ]])

                    for chat_id in authorized_chat_ids:
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=msg,
                            parse_mode='HTML',
                            reply_markup=keyboard
                        )

                    already_notified_ids.add(item['id'])

    except Exception as e:
        logger.exception(f"Ошибка при получении заказов: {e}")

# Обработка кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("done_"):
        item_id = query.data.split("_")[1]
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{API_BASE_URL}/mark_done/{item_id}/")
                response.raise_for_status()

            ready_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            old_text = query.message.text_html or query.message.text
            import re
            new_text = re.sub(
                r"⏳ <b>Статус:</b>.*",
                f"✅ <b>Статус:</b> Готово\n🕒 <b>Время готовности:</b> {ready_time}",
                old_text
            )

            await query.edit_message_text(
                text=new_text,
                parse_mode='HTML',
                reply_markup=None
            )

        except Exception as e:
            logger.exception(f"Ошибка при завершении заказа: {e}")
            await query.edit_message_text("❌ Ошибка при завершении заказа.")

# Запуск
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.job_queue.run_repeating(check_new_orders, interval=5)

    logger.info("Бот официанта запущен.")
    app.run_polling()

if __name__ == "__main__":
    main()
