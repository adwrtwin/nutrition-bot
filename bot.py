import os
import logging
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Получение переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Инициализация Supabase клиента
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        telegram_id = user.id
        user_name = user.first_name or "Пользователь"
        
        # Проверяем, есть ли пользователь в базе
        response = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
        
        if len(response.data) == 0:
            # Создаем нового пользователя
            trial_ends_at = (datetime.now() + timedelta(days=3)).isoformat()
            new_user = {
                "telegram_id": telegram_id,
                "name": user_name,
                "tariff": "trial",
                "trial_ends_at": trial_ends_at,
                "created_at": datetime.now().isoformat()
            }
            user_data = supabase.table("users").insert(new_user).execute()
            
            await update.message.reply_text(
                f"Привет {user_name}! 👋\n"
                f"Я бот-нутрициолог. У вас начался пробный период на 3 дня.\n\n"
                f"Напишите 'меню' для получения пробного меню или задайте вопрос о питании."
            )
        else:
            # Пользователь уже существует
            user_data = response.data[0]
            days_left = (datetime.fromisoformat(user_data['trial_ends_at']) - datetime.now()).days
            
            await update.message.reply_text(
                f"С возвращением, {user_name}! 🌟\n"
                f"У вас осталось {days_left} дней пробного периода.\n\n"
                f"Напишите 'меню' для получения меню."
            )
            
    except Exception as e:
        logger.error(f"Ошибка при сохранении пользователя: {e}")
        await update.message.reply_text("Привет! Я бот-нутрициолог. Напишите 'меню' для пробного дня.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        user_message = update.message.text
        
        # Сохраняем сообщение в историю (будет реализовано позже)
        
        if "меню" in user_message.lower():
            await send_trial_menu(update)
        else:
            await update.message.reply_text(
                "Пока я умею показывать меню и отвечать на базовые вопросы.\n"
                "Напишите 'меню' для получения пробного меню на день."
            )
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Произошла ошибка. Попробуйте еще раз.")

async def send_trial_menu(update: Update):
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
    await update.message.reply_text(menu_text)

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот запущен с интеграцией Supabase...")
    application.run_polling()

if __name__ == "__main__":
    main()
