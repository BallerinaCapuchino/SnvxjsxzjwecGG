#!/usr/bin/env python3
"""
HomeOS Backend Server with Telegram Bot API Storage
Хранение данных через Telegram Bot API для многопользовательской системы
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError
import asyncio
from functools import wraps

app = Flask(__name__)
CORS(app)  # Разрешить запросы из браузера

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
STORAGE_CHAT_ID = os.getenv('STORAGE_CHAT_ID', 'YOUR_CHAT_ID')  # Приватный канал для хранения

# Инициализация бота
bot = Bot(token=BOT_TOKEN)

# Префиксы для хранения разных типов данных
STORAGE_KEYS = {
    'bank_users': 'BANK_USERS_V11',
    'bank_history': 'BANK_HISTORY_V11',
    'bank_notes': 'BANK_NOTES_V11',
    'shop_users': 'SHOP_USERS_V1',
    'shop_products': 'SHOP_PRODUCTS_V1',
    'shop_stores': 'SHOP_STORES_V1',
    'shop_withdrawals': 'SHOP_WITHDRAWALS_V1',
    'myinfo_users': 'MYINFO_USERS_V1',
    'myinfo_records': 'MYINFO_RECORDS_V1',
    'myinfo_audit': 'MYINFO_AUDIT_V1',
    'mywork_users': 'MYWORK_USERS_V2',
    'mywork_shifts': 'MYWORK_SHIFTS_V2',
    'mywork_tasks': 'MYWORK_TASKS_V2',
    'mywork_running': 'MYWORK_RUNNING_V1'
}

def async_route(f):
    """Декоратор для async функций в Flask"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

async def telegram_get(key):
    """Получить данные из Telegram"""
    try:
        # Ищем сообщение с нужным ключом в закрепленных
        message_text = f"#{key}\n"
        
        # Получаем последние сообщения из канала
        updates = await bot.get_updates(limit=100)
        
        for update in reversed(updates):
            if update.channel_post and update.channel_post.text:
                if update.channel_post.text.startswith(message_text):
                    data_json = update.channel_post.text[len(message_text):]
                    return json.loads(data_json)
        
        return None
    except Exception as e:
        print(f"Error reading from Telegram: {e}")
        return None

async def telegram_set(key, data):
    """Сохранить данные в Telegram"""
    try:
        message_text = f"#{key}\n{json.dumps(data, ensure_ascii=False, indent=2)}"
        
        # Отправляем новое сообщение
        await bot.send_message(
            chat_id=STORAGE_CHAT_ID,
            text=message_text
        )
        
        return True
    except TelegramError as e:
        print(f"Error writing to Telegram: {e}")
        return False

# ==================== BANK API ====================

@app.route('/api/bank/users', methods=['GET'])
@async_route
async def get_bank_users():
    """Получить всех пользователей банка"""
    users = await telegram_get(STORAGE_KEYS['bank_users']) or []
    return jsonify(users)

@app.route('/api/bank/users', methods=['POST'])
@async_route
async def save_bank_users():
    """Сохранить пользователей банка"""
    users = request.json
    success = await telegram_set(STORAGE_KEYS['bank_users'], users)
    return jsonify({'success': success})

@app.route('/api/bank/history', methods=['GET'])
@async_route
async def get_bank_history():
    """Получить историю переводов"""
    history = await telegram_get(STORAGE_KEYS['bank_history']) or []
    return jsonify(history)

@app.route('/api/bank/history', methods=['POST'])
@async_route
async def save_bank_history():
    """Сохранить историю переводов"""
    history = request.json
    success = await telegram_set(STORAGE_KEYS['bank_history'], history)
    return jsonify({'success': success})

@app.route('/api/bank/notes', methods=['GET'])
@async_route
async def get_bank_notes():
    """Получить уведомления"""
    notes = await telegram_get(STORAGE_KEYS['bank_notes']) or {}
    return jsonify(notes)

@app.route('/api/bank/notes', methods=['POST'])
@async_route
async def save_bank_notes():
    """Сохранить уведомления"""
    notes = request.json
    success = await telegram_set(STORAGE_KEYS['bank_notes'], notes)
    return jsonify({'success': success})

# ==================== SHOP API ====================

@app.route('/api/shop/users', methods=['GET'])
@async_route
async def get_shop_users():
    """Получить пользователей магазина"""
    users = await telegram_get(STORAGE_KEYS['shop_users']) or []
    return jsonify(users)

@app.route('/api/shop/users', methods=['POST'])
@async_route
async def save_shop_users():
    """Сохранить пользователей магазина"""
    users = request.json
    success = await telegram_set(STORAGE_KEYS['shop_users'], users)
    return jsonify({'success': success})

@app.route('/api/shop/products', methods=['GET'])
@async_route
async def get_shop_products():
    """Получить товары"""
    products = await telegram_get(STORAGE_KEYS['shop_products']) or []
    return jsonify(products)

@app.route('/api/shop/products', methods=['POST'])
@async_route
async def save_shop_products():
    """Сохранить товары"""
    products = request.json
    success = await telegram_set(STORAGE_KEYS['shop_products'], products)
    return jsonify({'success': success})

@app.route('/api/shop/stores', methods=['GET'])
@async_route
async def get_shop_stores():
    """Получить магазины"""
    stores = await telegram_get(STORAGE_KEYS['shop_stores']) or []
    return jsonify(stores)

@app.route('/api/shop/stores', methods=['POST'])
@async_route
async def save_shop_stores():
    """Сохранить магазины"""
    stores = request.json
    success = await telegram_set(STORAGE_KEYS['shop_stores'], stores)
    return jsonify({'success': success})

@app.route('/api/shop/withdrawals', methods=['GET'])
@async_route
async def get_shop_withdrawals():
    """Получить запросы на вывод"""
    withdrawals = await telegram_get(STORAGE_KEYS['shop_withdrawals']) or []
    return jsonify(withdrawals)

@app.route('/api/shop/withdrawals', methods=['POST'])
@async_route
async def save_shop_withdrawals():
    """Сохранить запросы на вывод"""
    withdrawals = request.json
    success = await telegram_set(STORAGE_KEYS['shop_withdrawals'], withdrawals)
    return jsonify({'success': success})

# ==================== MYINFO API ====================

@app.route('/api/myinfo/users', methods=['GET'])
@async_route
async def get_myinfo_users():
    """Получить пользователей MyInfo"""
    users = await telegram_get(STORAGE_KEYS['myinfo_users']) or []
    return jsonify(users)

@app.route('/api/myinfo/users', methods=['POST'])
@async_route
async def save_myinfo_users():
    """Сохранить пользователей MyInfo"""
    users = request.json
    success = await telegram_set(STORAGE_KEYS['myinfo_users'], users)
    return jsonify({'success': success})

@app.route('/api/myinfo/records', methods=['GET'])
@async_route
async def get_myinfo_records():
    """Получить записи MyInfo"""
    records = await telegram_get(STORAGE_KEYS['myinfo_records']) or {}
    return jsonify(records)

@app.route('/api/myinfo/records', methods=['POST'])
@async_route
async def save_myinfo_records():
    """Сохранить записи MyInfo"""
    records = request.json
    success = await telegram_set(STORAGE_KEYS['myinfo_records'], records)
    return jsonify({'success': success})

@app.route('/api/myinfo/audit', methods=['GET'])
@async_route
async def get_myinfo_audit():
    """Получить аудит MyInfo"""
    audit = await telegram_get(STORAGE_KEYS['myinfo_audit']) or []
    return jsonify(audit)

@app.route('/api/myinfo/audit', methods=['POST'])
@async_route
async def save_myinfo_audit():
    """Сохранить аудит MyInfo"""
    audit = request.json
    success = await telegram_set(STORAGE_KEYS['myinfo_audit'], audit)
    return jsonify({'success': success})

# ==================== MYWORK API ====================

@app.route('/api/mywork/users', methods=['GET'])
@async_route
async def get_mywork_users():
    """Получить пользователей MyWork"""
    users = await telegram_get(STORAGE_KEYS['mywork_users']) or []
    return jsonify(users)

@app.route('/api/mywork/users', methods=['POST'])
@async_route
async def save_mywork_users():
    """Сохранить пользователей MyWork"""
    users = request.json
    success = await telegram_set(STORAGE_KEYS['mywork_users'], users)
    return jsonify({'success': success})

@app.route('/api/mywork/shifts', methods=['GET'])
@async_route
async def get_mywork_shifts():
    """Получить смены MyWork"""
    shifts = await telegram_get(STORAGE_KEYS['mywork_shifts']) or {}
    return jsonify(shifts)

@app.route('/api/mywork/shifts', methods=['POST'])
@async_route
async def save_mywork_shifts():
    """Сохранить смены MyWork"""
    shifts = request.json
    success = await telegram_set(STORAGE_KEYS['mywork_shifts'], shifts)
    return jsonify({'success': success})

@app.route('/api/mywork/tasks', methods=['GET'])
@async_route
async def get_mywork_tasks():
    """Получить задачи MyWork"""
    tasks = await telegram_get(STORAGE_KEYS['mywork_tasks']) or {}
    return jsonify(tasks)

@app.route('/api/mywork/tasks', methods=['POST'])
@async_route
async def save_mywork_tasks():
    """Сохранить задачи MyWork"""
    tasks = request.json
    success = await telegram_set(STORAGE_KEYS['mywork_tasks'], tasks)
    return jsonify({'success': success})

@app.route('/api/mywork/running', methods=['GET'])
@async_route
async def get_mywork_running():
    """Получить активные смены"""
    running = await telegram_get(STORAGE_KEYS['mywork_running']) or {}
    return jsonify(running)

@app.route('/api/mywork/running', methods=['POST'])
@async_route
async def save_mywork_running():
    """Сохранить активные смены"""
    running = request.json
    success = await telegram_set(STORAGE_KEYS['mywork_running'], running)
    return jsonify({'success': success})

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Проверка работоспособности сервера"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'bot_configured': BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE',
        'storage_configured': STORAGE_CHAT_ID != 'YOUR_CHAT_ID'
    })

@app.route('/api/init', methods=['POST'])
@async_route
async def initialize_storage():
    """Инициализация хранилища (только для первого запуска)"""
    try:
        # Создаем начальные данные для банка
        initial_bank_users = [
            {'username': 'Max', 'password': '12345', 'isAdmin': True, 'balance': 0, 'online': False, 'deleted': False}
        ]
        
        await telegram_set(STORAGE_KEYS['bank_users'], initial_bank_users)
        await telegram_set(STORAGE_KEYS['bank_history'], [])
        await telegram_set(STORAGE_KEYS['bank_notes'], {})
        
        # Создаем начальные данные для магазина
        initial_shop_users = [
            {'id': 1, 'username': 'max', 'password': '12345', 'balance': 1000000, 'role': 'admin'}
        ]
        
        initial_products = [
            {'id': 1, 'storeId': 1, 'title': 'Смартфон Premium', 'description': 'Флагманский смартфон', 'price': 2500, 'stock': 5, 'category': 'electronics', 'icon': '📱', 'soldCount': 0},
            {'id': 2, 'storeId': 1, 'title': 'Ноутбук Pro', 'description': 'Мощный ноутбук', 'price': 5000, 'stock': 3, 'category': 'electronics', 'icon': '💻', 'soldCount': 0},
            {'id': 3, 'storeId': 1, 'title': 'Наушники Wireless', 'description': 'Беспроводные наушники', 'price': 800, 'stock': 10, 'category': 'electronics', 'icon': '🎧', 'soldCount': 0},
        ]
        
        initial_stores = [
            {'id': 1, 'ownerId': 1, 'name': 'MT Shop', 'soldCount': 0, 'revenue': 0, 'withdrawalBalance': 0}
        ]
        
        await telegram_set(STORAGE_KEYS['shop_users'], initial_shop_users)
        await telegram_set(STORAGE_KEYS['shop_products'], initial_products)
        await telegram_set(STORAGE_KEYS['shop_stores'], initial_stores)
        await telegram_set(STORAGE_KEYS['shop_withdrawals'], [])
        
        # MyInfo
        await telegram_set(STORAGE_KEYS['myinfo_users'], initial_shop_users)
        await telegram_set(STORAGE_KEYS['myinfo_records'], {})
        await telegram_set(STORAGE_KEYS['myinfo_audit'], [])
        
        # MyWork
        await telegram_set(STORAGE_KEYS['mywork_users'], initial_shop_users)
        await telegram_set(STORAGE_KEYS['mywork_shifts'], {})
        await telegram_set(STORAGE_KEYS['mywork_tasks'], {})
        await telegram_set(STORAGE_KEYS['mywork_running'], {})
        
        return jsonify({'success': True, 'message': 'Storage initialized'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ ОШИБКА: Установите BOT_TOKEN в переменных окружения")
        print("export BOT_TOKEN='ваш_токен'")
        print("export STORAGE_CHAT_ID='@ваш_канал'")
        exit(1)
    
    print("🚀 HomeOS Backend Server")
    print(f"📡 Bot Token: {BOT_TOKEN[:10]}...")
    print(f"💾 Storage Chat: {STORAGE_CHAT_ID}")
    print("✅ Server running on http://localhost:5000")
    print("📖 API Docs: http://localhost:5000/api/health")
    
    app.run(host='0.0.0.0', port=5000, debug=True)