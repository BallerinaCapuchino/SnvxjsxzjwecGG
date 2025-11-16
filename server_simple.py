#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HomeOS Multi-User Backend Server - Simplified Version
Локальное хранилище с возможностью синхронизации с GitHub
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import os
import hashlib
import hmac
from datetime import datetime
from urllib.parse import unquote
from functools import wraps

# Fix Windows encoding
if os.name == 'nt':
    import codecs
    import sys
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', '3f8a9c2b5d7e1f4a6c8b0d2e4f6a8c0b')
CORS(app, supports_credentials=True, origins=['*'])

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
DATA_DIR = 'server_data'  # Local data directory

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Supported languages
TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome', 'login': 'Login', 'logout': 'Logout',
        'register': 'Register', 'balance': 'Balance', 'transfer': 'Transfer',
        'history': 'History', 'settings': 'Settings', 'admin': 'Admin',
        'users': 'Users', 'success': 'Success', 'error': 'Error',
    },
    'ru': {
        'welcome': 'Добро пожаловать', 'login': 'Вход', 'logout': 'Выход',
        'register': 'Регистрация', 'balance': 'Баланс', 'transfer': 'Перевод',
        'history': 'История', 'settings': 'Настройки', 'admin': 'Администратор',
        'users': 'Пользователи', 'success': 'Успешно', 'error': 'Ошибка',
    }
}

# ==================== LOCAL STORAGE ====================

def get_data(filename):
    """Get data from local JSON file"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def save_data(filename, data):
    """Save data to local JSON file"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error writing {filename}: {e}")
        return False

# ==================== AUTHENTICATION ====================

def verify_telegram_auth(init_data_raw):
    """Verify Telegram Web App authentication"""
    try:
        params = {}
        for item in init_data_raw.split('&'):
            if '=' in item:
                key, value = item.split('=', 1)
                params[key] = unquote(value)
        
        received_hash = params.pop('hash', '')
        data_check_string_parts = [f"{key}={params[key]}" for key in sorted(params.keys())]
        data_check_string = '\n'.join(data_check_string_parts)
        
        secret_key = hmac.new(b'WebAppData', BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        
        if calculated_hash != received_hash:
            return None
        
        if 'user' in params:
            return json.loads(params['user'])
        return None
    except Exception as e:
        print(f"Auth error: {e}")
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== API ROUTES ====================

@app.route('/api/auth/telegram', methods=['POST'])
def auth_telegram():
    """Authenticate user via Telegram Web App"""
    try:
        data = request.json
        init_data = data.get('initData')
        
        if not init_data:
            return jsonify({'success': False, 'error': 'No init data'}), 400
        
        user_data = verify_telegram_auth(init_data)
        if not user_data:
            return jsonify({'success': False, 'error': 'Invalid auth'}), 401
        
        session['user_id'] = user_data['id']
        session['username'] = user_data.get('username') or user_data.get('first_name') or f"user_{user_data['id']}"
        session['first_name'] = user_data.get('first_name', '')
        
        # Get or create user
        users = get_data('users.json') or []
        user = next((u for u in users if u['telegram_id'] == user_data['id']), None)
        
        if not user:
            user = {
                'telegram_id': user_data['id'],
                'username': session['username'],
                'first_name': session['first_name'],
                'created_at': datetime.now().isoformat(),
                'language': 'ru'
            }
            users.append(user)
            save_data('users.json', users)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_data['id'],
                'username': session['username'],
                'first_name': session['first_name']
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/check', methods=['GET'])
def auth_check():
    """Check authentication"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {'id': session['user_id'], 'username': session['username']}
        })
    return jsonify({'authenticated': False})

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Logout"""
    session.clear()
    return jsonify({'success': True})

# ==================== TRANSLATIONS ====================

@app.route('/api/translations/<lang>', methods=['GET'])
def get_translations(lang):
    """Get translations"""
    return jsonify(TRANSLATIONS.get(lang, TRANSLATIONS['en']))

# ==================== BANK API ====================

@app.route('/api/bank/users', methods=['GET'])
@require_auth
def get_bank_users():
    """Get all bank users"""
    users = get_data('bank_users.json') or []
    return jsonify(users)

@app.route('/api/bank/my-account', methods=['GET'])
@require_auth
def get_my_bank_account():
    """Get current user's account"""
    users = get_data('bank_users.json') or []
    user = next((u for u in users if u.get('telegram_id') == session['user_id']), None)
    
    if not user:
        user = {
            'telegram_id': session['user_id'],
            'username': session['username'],
            'balance': 10000,
            'isAdmin': False,
            'online': True,
            'deleted': False
        }
        users.append(user)
        save_data('bank_users.json', users)
    
    return jsonify(user)

@app.route('/api/bank/transfer', methods=['POST'])
@require_auth
def bank_transfer():
    """Make transfer"""
    data = request.json
    to_username = data.get('to')
    amount = float(data.get('amount', 0))
    comment = data.get('comment', '')
    
    if amount <= 0:
        return jsonify({'success': False, 'error': 'Invalid amount'}), 400
    
    users = get_data('bank_users.json') or []
    from_user = next((u for u in users if u.get('telegram_id') == session['user_id']), None)
    to_user = next((u for u in users if u['username'] == to_username), None)
    
    if not from_user or not to_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    if from_user['balance'] < amount:
        return jsonify({'success': False, 'error': 'Insufficient funds'}), 400
    
    from_user['balance'] -= amount
    to_user['balance'] += amount
    save_data('bank_users.json', users)
    
    history = get_data('bank_history.json') or []
    history.insert(0, {
        'time': datetime.now().isoformat(),
        'from': from_user['username'],
        'to': to_user['username'],
        'amount': amount,
        'comment': comment
    })
    save_data('bank_history.json', history)
    
    return jsonify({'success': True, 'balance': from_user['balance']})

@app.route('/api/bank/history', methods=['GET'])
@require_auth
def get_bank_history():
    """Get history"""
    history = get_data('bank_history.json') or []
    my_username = session['username']
    my_history = [h for h in history if h['from'] == my_username or h['to'] == my_username]
    return jsonify(my_history[:100])

# ==================== SHOP API ====================

@app.route('/api/shop/products', methods=['GET'])
def get_shop_products():
    """Get products"""
    return jsonify(get_data('shop_products.json') or [])

@app.route('/api/shop/my-store', methods=['GET'])
@require_auth
def get_my_store():
    """Get my store"""
    stores = get_data('shop_stores.json') or []
    store = next((s for s in stores if s.get('owner_telegram_id') == session['user_id']), None)
    return jsonify(store)

@app.route('/api/shop/purchase', methods=['POST'])
@require_auth
def shop_purchase():
    """Purchase products"""
    data = request.json
    cart = data.get('cart', [])
    
    if not cart:
        return jsonify({'success': False, 'error': 'Empty cart'}), 400
    
    products = get_data('shop_products.json') or []
    total = 0
    
    for item in cart:
        product = next((p for p in products if p['id'] == item['id']), None)
        if not product or product['stock'] < item['qty']:
            return jsonify({'success': False, 'error': 'Product unavailable'}), 400
        total += product['price'] * item['qty']
    
    users = get_data('bank_users.json') or []
    user = next((u for u in users if u.get('telegram_id') == session['user_id']), None)
    
    if not user or user['balance'] < total:
        return jsonify({'success': False, 'error': 'Insufficient funds'}), 400
    
    for item in cart:
        product = next((p for p in products if p['id'] == item['id']), None)
        product['stock'] -= item['qty']
        product['soldCount'] = product.get('soldCount', 0) + item['qty']
    
    user['balance'] -= total
    
    save_data('shop_products.json', products)
    save_data('bank_users.json', users)
    
    return jsonify({'success': True, 'balance': user['balance']})

# ==================== MYWORK API ====================

@app.route('/api/mywork/start-shift', methods=['POST'])
@require_auth
def start_shift():
    """Start shift"""
    running = get_data('mywork_running.json') or {}
    username = session['username']
    
    if username in running:
        return jsonify({'success': False, 'error': 'Shift already started'}), 400
    
    running[username] = datetime.now().isoformat()
    save_data('mywork_running.json', running)
    return jsonify({'success': True})

@app.route('/api/mywork/stop-shift', methods=['POST'])
@require_auth
def stop_shift():
    """Stop shift"""
    data = request.json
    minutes = data.get('minutes', 0)
    pay = data.get('pay', 0)
    
    running = get_data('mywork_running.json') or {}
    username = session['username']
    
    if username not in running:
        return jsonify({'success': False, 'error': 'No active shift'}), 400
    
    start_time = running.pop(username)
    save_data('mywork_running.json', running)
    
    shifts = get_data('mywork_shifts.json') or {}
    if username not in shifts:
        shifts[username] = []
    
    shifts[username].insert(0, {
        'start': start_time,
        'end': datetime.now().isoformat(),
        'minutes': minutes,
        'pay': pay
    })
    save_data('mywork_shifts.json', shifts)
    
    return jsonify({'success': True})

@app.route('/api/mywork/shifts', methods=['GET'])
@require_auth
def get_shifts():
    """Get shifts"""
    shifts = get_data('mywork_shifts.json') or {}
    return jsonify(shifts.get(session['username'], []))

# ==================== MYINFO API ====================

@app.route('/api/myinfo/records', methods=['GET'])
@require_auth
def get_myinfo_records():
    """Get records"""
    records = get_data('myinfo_records.json') or {}
    return jsonify(records.get(session['username'], {}))

@app.route('/api/myinfo/records', methods=['POST'])
@require_auth
def save_myinfo_records():
    """Save records"""
    data = request.json
    records = get_data('myinfo_records.json') or {}
    records[session['username']] = data
    save_data('myinfo_records.json', records)
    return jsonify({'success': True})

# ==================== HEALTH & INIT ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'storage': 'local',
        'data_dir': os.path.abspath(DATA_DIR),
        'bot_configured': BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'
    })

@app.route('/api/init', methods=['POST'])
def initialize_storage():
    """Initialize storage"""
    try:
        save_data('users.json', [])
        save_data('bank_users.json', [])
        save_data('bank_history.json', [])
        save_data('shop_products.json', [
            {'id': 1, 'title': 'Смартфон Premium', 'description': 'Флагманский смартфон', 'price': 2500, 'stock': 5, 'category': 'electronics', 'icon': '📱', 'soldCount': 0},
            {'id': 2, 'title': 'Ноутбук Pro', 'description': 'Мощный ноутбук', 'price': 5000, 'stock': 3, 'category': 'electronics', 'icon': '💻', 'soldCount': 0},
            {'id': 3, 'title': 'Наушники Wireless', 'description': 'Беспроводные', 'price': 800, 'stock': 10, 'category': 'electronics', 'icon': '🎧', 'soldCount': 0},
        ])
        save_data('shop_stores.json', [])
        save_data('mywork_shifts.json', {})
        save_data('mywork_running.json', {})
        save_data('myinfo_records.json', {})
        
        return jsonify({'success': True, 'message': 'Storage initialized', 'location': os.path.abspath(DATA_DIR)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("HomeOS Multi-User Server - Simple Version")
    print("=" * 60)
    print("")
    print(f"[*] Data Storage: {os.path.abspath(DATA_DIR)}")
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("[!] BOT_TOKEN не настроен")
        print("    Telegram аутентификация недоступна")
        print("    Для работы можно использовать без Telegram")
    else:
        print(f"[OK] Bot Token: {BOT_TOKEN[:10]}...")
    
    print("")
    print("[OK] Server running on http://0.0.0.0:5000")
    print("[*] Health check: http://localhost:5000/api/health")
    print("[*] Initialize: curl -X POST http://localhost:5000/api/init")
    print("")
    print("Press Ctrl+C to stop")
    print("")
    
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)