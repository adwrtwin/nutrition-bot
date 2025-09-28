import os
import logging
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка Flask для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Nutrition Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Временное хранилище пользователей
user_data = {}

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_name = user.first_name or "Пользователь"
    
    # Сохраняем пользователя во временное хранилище
    user_data[user.id] = {
        "name": user_name,
        "joined_date": "2024-01-20"
    }
    
    update.message.reply_text(
        f"Привет {user_name}! 👋\n"
        f"Я бот-нутрициолог. У вас начался пробный период на 3 дня.\n\n"
        f"Напишите 'меню' для получения пробного меню."
    )

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
        update.message.reply_text('Пока я умею только показывать меню. Напишите "меню"')

def main():
    # Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Создаем Updater (для версии 13.15)
    updater = Updater(BOT_TOKEN, use_context=True)
    
    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher
    
    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    
    # Регистрируем обработчик текстовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    # Запускаем бота
    print("Бот запущен с версией python-telegram-bot 13.15...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
