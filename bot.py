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

# Файловое хранилище
DATA_FILE = "user_data.json"

def load_user_data():
    """Загружает данные пользователей из JSON файла"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
        return {}

def save_user_data(data):
    """Сохраняет данные пользователей в JSON файл"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
        return False

def get_user(user_id):
    """Получает данные пользователя"""
    data = load_user_data()
    return data.get(str(user_id))

def save_user(user_id, user_data):
    """Сохраняет данные пользователя"""
    data = load_user_data()
    data[str(user_id)] = user_data
    return save_user_data(data)

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_id = user.id
    user_name = user.first_name or "Пользователь"
    
    # Проверяем существующего пользователя
    existing_user = get_user(user_id)
    
    if existing_user:
        # Пользователь уже существует
        trial_ends = datetime.fromisoformat(existing_user['trial_ends'])
        days_left = (trial_ends - datetime.now()).days
        
        if days_left > 0:
            message = (
                f"С возвращением, {user_name}! 🌟\n"
                f"У вас осталось {days_left} дней пробного периода.\n\n"
                f"Напишите 'меню' для получения меню."
            )
        else:
            message = (
                f"С возвращением, {user_name}! ⏰\n"
                f"Ваш пробный период завершен.\n\n"
                f"Напишите 'тарифы' для перехода на полную версию."
            )
    else:
        # Новый пользователь
        trial_ends = (datetime.now() + timedelta(days=3)).isoformat()
        new_user_data = {
            "name": user_name,
            "telegram_id": user_id,
            "joined_date": datetime.now().isoformat(),
            "trial_ends": trial_ends,
            "tariff": "trial",
            "goals": [],
            "allergies": [],
            "last_active": datetime.now().isoformat()
        }
        
        if save_user(user_id, new_user_data):
            message = (
                f"Привет {user_name}! 👋\n"
                f"Я бот-нутрициолог. У вас начался пробный период на 3 дня.\n\n"
                f"Давайте познакомимся! Ответьте на несколько вопросов для персонализации:\n\n"
                f"1. Какие у вас цели? (похудение, набор массы, поддержание, здоровье)\n"
                f"2. Есть ли аллергии или ограничения?\n"
                f"3. Какой уровень активности? (низкий, средний, высокий)\n\n"
                f"Или напишите 'меню' для получения пробного меню."
            )
        else:
            message = (
                f"Привет {user_name}! 👋\n"
                f"Я бот-нутрициолог. У вас начался пробный период на 3 дня.\n\n"
                f"Напишите 'меню' для получения пробного меню."
            )
    
    update.message.reply_text(message)

def handle_message(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_id = user.id
    text = update.message.text.lower()
    
    # Обновляем время последней активности
    user_data = get_user(user_id)
    if user_data:
        user_data["last_active"] = datetime.now().isoformat()
        save_user(user_id, user_data)
    
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
    
    elif "тарифы" in text:
        tariffs_text = """
💎 ДОСТУПНЫЕ ТАРИФЫ:

🔹 ПРОБНЫЙ (3 дня) - БЕСПЛАТНО
• Базовые рекомендации
• Пробное меню на 1 день

🔹 ПЕРСОНАЛЬНЫЙ (990 руб./мес)
• Индивидуальное меню на каждую неделю
• Список покупок с альтернативами
• Поддержка по вопросам питания

🔹 СЕМЕЙНЫЙ (2500 руб./мес)
• До 5 пользователей
• Общий оптимизированный список покупок
• Индивидуальные меню для каждого

Для перехода на тариф напишите 'хочу тариф'
"""
        update.message.reply_text(tariffs_text)
    
    elif "хочу тариф" in text:
        update.message.reply_text(
            "Отлично! Для подключения тарифа напишите нам:\n"
            "• Желаемый тариф (Персональный/Семейный)\n"
            "• Ваши контактные данные\n\n"
            "Мы свяжемся с вами в ближайшее время!"
        )
    
    else:
        # Анализ сообщения для сбора данных
        user_data = get_user(user_id)
        if user_data:
            # Если пользователь новый и еще не указал цели
            if not user_data.get("goals"):
                if any(word in text for word in ["похудение", "похудеть", "сбросить вес"]):
                    user_data.setdefault("goals", []).append("weight_loss")
                    save_user(user_id, user_data)
                    update.message.reply_text("✅ Записал цель: похудение. Есть еще цели?")
                    return
                elif any(word in text for word in ["набор", "масса", "мышцы"]):
                    user_data.setdefault("goals", []).append("muscle_gain")
                    save_user(user_id, user_data)
                    update.message.reply_text("✅ Записал цель: набор мышечной массы. Есть еще цели?")
                    return
                elif any(word in text for word in ["поддержание", "форма"]):
                    user_data.setdefault("goals", []).append("maintenance")
                    save_user(user_id, user_data)
                    update.message.reply_text("✅ Записал цель: поддержание формы. Есть еще цели?")
                    return
        
        update.message.reply_text(
            "Напишите 'меню' для получения пробного меню\n"
            "Или 'тарифы' для просмотра доступных тарифов"
        )

def main():
    # Создаем файл данных если его нет
    if not os.path.exists(DATA_FILE):
        save_user_data({})
        print("Создан новый файл данных")
    
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    updater = Updater(BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    print("Бот запущен с JSON хранилищем...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
