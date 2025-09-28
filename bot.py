import os
import logging
import threading
import json
from datetime import datetime, timedelta
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

app = Flask(__name__)

@app.route('/')
def home():
    return "Nutrition Bot is running!", 200

def run_flask():
    if os.environ.get('RENDER'):
        os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Простое хранилище в памяти (временно)
user_storage = {}

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "Пользователь"
    
    # Сохраняем пользователя
    if user_id not in user_storage:
        user_storage[user_id] = {
            "name": user_name,
            "joined_date": datetime.now().isoformat(),
            "trial_ends": (datetime.now() + timedelta(days=3)).isoformat()
        }
    
    user_data = user_storage[user_id]
    trial_ends = datetime.fromisoformat(user_data['trial_ends'])
    days_left = (trial_ends - datetime.now()).days
    
    message = (
        f"Привет {user_name}! 👋\n"
        f"Я бот-нутрициолог. У вас начался пробный период на 3 дня.\n"
        f"Осталось дней: {max(days_left, 0)}\n\n"
        f"Напишите 'меню' для получения пробного меню."
    )
    
    update.message.reply_text(message)

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text.lower()
    
    if "меню" in text:
        menu_text = """
🍽️ ПРОБНОЕ МЕНЮ НА ДЕНЬ:

ЗАВТРАК: Белковый омлет
• 2 яйца + 100г творога + овощи
• КБЖУ: 320 ккал • Б: 28г • Ж: 18г • У: 12г

ОБЕД: Куриная грудка с гречкой  
• 150г курицы + 100г гречки + салат
• КБЖУ: 450 ккал • Б: 35г • Ж: 12г • У: 45г

УЖИН: Рыба на пару с овощами
• 200г трески + брокколи + морковь
• КБЖУ: 280 ккал • Б: 25г • Ж: 8г • У: 20г

📋 В полной версии вы получите:
• Меню на неделю с новыми блюдами
• Список покупок с экономией
• Персональные рекомендации
"""
        update.message.reply_text(menu_text)
    else:
        update.message.reply_text('Напишите "меню" для получения пробного меню.')

def main():
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    print("Бот запущен (упрощенная версия)...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
