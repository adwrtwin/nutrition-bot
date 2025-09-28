import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Получение токена из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

def start(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение когда получена команда /start"""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Привет {user.mention_markdown_v2()}\! Я бот\-нутрициолог\. Напишите "меню" для пробного дня\.'
    )

def help_command(update: Update, context: CallbackContext) -> None:
    """Отправляет сообщение когда получена команда /help"""
    update.message.reply_text('Напишите "меню" для получения пробного меню.')

def handle_message(update: Update, context: CallbackContext) -> None:
    """Обрабатывает входящие текстовые сообщения"""
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
"""
        update.message.reply_text(menu_text)
    else:
        update.message.reply_text('Пока я умею только показывать меню. Напишите "меню"')

def main() -> None:
    """Запускает бота."""
    # Создаем Updater и передаем ему токен бота.
    updater = Updater(BOT_TOKEN)

    # Получаем диспетчер для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрируем обработчики команд
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # Регистрируем обработчик текстовых сообщений
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # Запускаем бота
    updater.start_polling()

    # Запускаем бота до тех пор, пока пользователь не остановит его (Ctrl+C)
    updater.idle()

if __name__ == '__main__':
    main()
