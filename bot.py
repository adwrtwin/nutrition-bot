import os
import logging
import threading
from datetime import datetime, timedelta
from flask import Flask
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from supabase import create_client, Client

# Настройка Flask для Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Nutrition Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

def run_flask():
    # Отключаем логи разработки в продакшене
    import os
    if os.environ.get('RENDER'):
        os.environ['WERKZEUG_RUN_MAIN'] = 'true'
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Инициализация Supabase клиента
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

def save_user_to_supabase(telegram_id, user_name):
    """Сохраняет пользователя в Supabase"""
    try:
        if not supabase:
            logger.error("Supabase client not available")
            return None
            
        # Проверяем, есть ли пользователь уже в базе
        response = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
        
        if len(response.data) > 0:
            logger.info(f"User {telegram_id} already exists in database")
            return response.data[0]
        
        # Создаем нового пользователя
        trial_ends_at = (datetime.now() + timedelta(days=3)).isoformat()
        new_user = {
            "telegram_id": telegram_id,
            "name": user_name,
            "tariff": "trial",
            "trial_ends_at": trial_ends_at,
            "created_at": datetime.now().isoformat()
        }
        
        result = supabase.table("users").insert(new_user).execute()
        
        if len(result.data) > 0:
            logger.info(f"User {telegram_id} saved to Supabase")
            return result.data[0]
        else:
            logger.error(f"Failed to save user {telegram_id} to Supabase")
            return None
            
    except Exception as e:
        logger.error(f"Error saving user to Supabase: {e}")
        return None

def get_user_from_supabase(telegram_id):
    """Получает пользователя из Supabase"""
    try:
        if not supabase:
            return None
            
        response = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
        
        if len(response.data) > 0:
            return response.data[0]
        return None
        
    except Exception as e:
        logger.error(f"Error getting user from Supabase: {e}")
        return None

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    telegram_id = user.id
    user_name = user.first_name or "Пользователь"
    
    # Сохраняем пользователя в Supabase
    user_data = save_user_to_supabase(telegram_id, user_name)
    
    if user_data:
        # Пользователь сохранен в базе
        trial_ends_at = datetime.fromisoformat(user_data['trial_ends_at'].replace('Z', '+00:00'))
        days_left = (trial_ends_at - datetime.now()).days
        
        if days_left > 0:
            message = (
                f"Привет {user_name}! 👋\n"
                f"Я бот-нутрициолог. У вас начался пробный период на 3 дня.\n"
                f"Осталось дней: {days_left}\n\n"
                f"Напишите 'меню' для получения пробного меню."
            )
        else:
            message = (
                f"С возвращением, {user_name}! ⏰\n"
                f"Ваш пробный период завершен.\n\n"
                f"Перейдите на полный тариф для продолжения использования."
            )
    else:
        # Ошибка базы данных, но бот продолжает работать
        message = (
            f"Привет {user_name}! 👋\n"
            f"Я бот-нутрициолог. У вас начался пробный период на 3 дня.\n\n"
            f"Напишите 'меню' для получения пробного меню."
        )
    
    update.message.reply_text(message)

def handle_message(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    text = update.message.text.lower()
    
    # Проверяем статус пользователя в базе
    user_data = get_user_from_supabase(user.id)
    
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
    print("Бот запущен с Supabase интеграцией...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
