import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я бот-нутрициолог. Напишите 'меню' для пробного дня.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_message = update.message.text
        
        if "меню" in user_message.lower():
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
"""
            await update.message.reply_text(menu_text)
            return
            
        await update.message.reply_text("Пока я умею только показывать меню. Напишите 'меню'")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("Произошла ошибка")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()
