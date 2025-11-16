<<<<<<< HEAD
#!/usr/bin/env python3
"""
Telegram Bot для HomeOS Mini App
Запуск: python bot.py
"""

from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# Замените на ваш токен бота от @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# URL вашего Web App (замените на свой URL)
WEB_APP_URL = "https://yoursite.com/index.html"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Создаем кнопку с Web App
    keyboard = [
        [KeyboardButton(
            text="🏠 Запустить HomeOS",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        f"Добро пожаловать в HomeOS — твоя виртуальная операционная система!\n\n"
        f"🏦 Банк MTBank\n"
        f"🛒 Магазин MT Shop\n"
        f"💼 Моя работа\n"
        f"📋 Моя информация\n\n"
        f"Нажми на кнопку ниже, чтобы запустить:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "🔹 /start - Начать работу\n"
        "🔹 /help - Помощь\n\n"
        "Используй кнопку '🏠 Запустить HomeOS' для запуска приложения!"
    )

def main():
    """Запуск бота"""
    print("🤖 Запуск HomeOS бота...")
    
    # Проверка токена
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ОШИБКА: Установите токен бота в переменной BOT_TOKEN")
        print("Получить токен можно у @BotFather в Telegram")
        return
    
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    print("✅ Бот запущен! Нажмите Ctrl+C для остановки.")
    
    # Запускаем бота
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
=======
#!/usr/bin/env python3
"""
Telegram Bot для HomeOS Mini App
Запуск: python bot.py
"""

from telegram import Update, WebAppInfo, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
import os

# Замените на ваш токен бота от @BotFather
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"

# URL вашего Web App (замените на свой URL)
WEB_APP_URL = "https://yoursite.com/index.html"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Создаем кнопку с Web App
    keyboard = [
        [KeyboardButton(
            text="🏠 Запустить HomeOS",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ]
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        f"Добро пожаловать в HomeOS — твоя виртуальная операционная система!\n\n"
        f"🏦 Банк MTBank\n"
        f"🛒 Магазин MT Shop\n"
        f"💼 Моя работа\n"
        f"📋 Моя информация\n\n"
        f"Нажми на кнопку ниже, чтобы запустить:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    await update.message.reply_text(
        "🔹 /start - Начать работу\n"
        "🔹 /help - Помощь\n\n"
        "Используй кнопку '🏠 Запустить HomeOS' для запуска приложения!"
    )

def main():
    """Запуск бота"""
    print("🤖 Запуск HomeOS бота...")
    
    # Проверка токена
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ОШИБКА: Установите токен бота в переменной BOT_TOKEN")
        print("Получить токен можно у @BotFather в Telegram")
        return
    
    # Создаем приложение
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    
    print("✅ Бот запущен! Нажмите Ctrl+C для остановки.")
    
    # Запускаем бота
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
>>>>>>> a77a40cc6f5bcac98cc7737b8900369ddf442ef0
    main()