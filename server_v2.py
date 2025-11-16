#!/usr/bin/env python3
"""
HomeOS Multi-User Backend Server with GitHub Storage
Stores all data in GitHub repository for true multi-user support
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import json
import os
import base64
import hashlib
import hmac
from datetime import datetime
from urllib.parse import unquote
import requests
from functools import wraps

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'change-this-secret-key-in-production')
CORS(app, supports_credentials=True)

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'YOUR_GITHUB_TOKEN_HERE')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'username/repo')  # Format: "username/repository"
GITHUB_BRANCH = os.getenv('GITHUB_BRANCH', 'main')
DATA_PATH = 'data'  # Path in repository where data will be stored

# GitHub API Base URL
GITHUB_API = 'https://api.github.com'

# Supported languages
TRANSLATIONS = {
    'en': {
        'welcome': 'Welcome',
        'login': 'Login',
        'logout': 'Logout',
        'register': 'Register',
        'balance': 'Balance',
        'transfer': 'Transfer',
        'history': 'History',
        'settings': 'Settings',
        'admin': 'Admin',
        'users': 'Users',
        'success': 'Success',
        'error': 'Error',
    },
    'ru': {
        'welcome': 'Добро пожаловать',
        'login': 'Вход',
        'logout': 'Выход',
        'register': 'Регистрация',
        'balance': 'Баланс',
        'transfer': 'Перевод',
        'history': 'История',
        'settings': 'Настройки',
        'admin': 'Администратор',
        'users': 'Пользователи',
        'success': 'Успешно',
        'error': 'Ошибка',
    }
}

# ==================== GITHUB STORAGE ====================

def github_get_file(file_path):
    """Get file content from GitHub"""
    try:
        url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{DATA_PATH}/{file_path}"
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        params = {'ref': GITHUB_BRANCH}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 404:
            return None, None
        
        if response.status_code != 200:
            print(f"Error getting file from GitHub: {response.status_code} - {response.text}")
            return None, None
        
        data = response.json()
        content = base64.b64decode(data['content']).decode('utf-8')
        sha = data['sha']
        
        return json.loads(content), sha
    except Exception as e:
        print(f"Error reading from GitHub: {e}")
        return None, None

def github_put_file(file_path, content, sha=None):
    """Create or update file in GitHub"""
    try:
        url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{DATA_PATH}/{file_path}"
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        content_encoded = base64.b64encode(json.dumps(content, ensure_ascii=False, indent=2).encode('utf-8')).decode('utf-8')
        
        payload = {
            'message': f'Update {file_path}',
            'content': content_encoded,
            'branch': GITHUB_BRANCH
        }
        
        if sha:
            payload['sha'] = sha
        
        response = requests.put(url, headers=headers, json=payload)
        
        if response.status_code not in [200, 201]:
            print(f"Error writing to GitHub: {response.status_code} - {response.text}")
            return False
        
        return True
    except Exception as e:
        print(f"Error writing to GitHub: {e}")
        return False

# ==================== AUTHENTICATION ====================

def verify_telegram_auth(init_data_raw):
    """Verify Telegram Web App authentication"""
    try:
        # Parse init data
        params = {}
        for item in init_data_raw.split('&'):
            key, value = item.split('=', 1)
            params[key] = unquote(value)
        
        # Get hash and remove it from params
        data_check_string_parts = []
        received_hash = params.pop('hash', '')
        
        # Sort params and create data-check-string
        for key in sorted(params.keys()):
            data_check_string_parts.append(f"{key}={params[key]}")
        
        data_check_string = '\n'.join(data_check_string_parts)
        
        # Create secret key
        secret_key = hmac.new(
            b'WebAppData',
            BOT_TOKEN.encode(),
            hashlib.sha256
        ).digest()
        
        # Calculate hash
        calculated_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify hash
        if calculated_hash != received_hash:
            return None
        
        # Parse user data
        if 'user' in params:
            user_data = json.loads(params['user'])
            return user_data
        
        return None
    except Exception as e:
        print(f"Error verifying Telegram auth: {e}")
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
            return jsonify({'success': False, 'error': 'No init data provided'}), 400
        
        user_data = verify_telegram_auth(init_data)
        
        if not user_data:
            return jsonify({'success': False, 'error': 'Invalid authentication'}), 401
        
        # Store user session
        session['user_id'] = user_data['id']
        session['username'] = user_data.get('username') or user_data.get('first_name') or f"user_{user_data['id']}"
        session['first_name'] = user_data.get('first_name', '')
        session['last_name'] = user_data.get('last_name', '')
        
        # Get or create user in database
        users, sha = github_get_file('users.json')
        if users is None:
            users = []
        
        # Find or create user
        user = next((u for u in users if u['telegram_id'] == user_data['id']), None)
        
        if not user:
            # Create new user
            user = {
                'telegram_id': user_data['id'],
                'username': session['username'],
                'first_name': session['first_name'],
                'last_name': session['last_name'],
                'created_at': datetime.now().isoformat(),
                'language': 'ru'
            }
            users.append(user)
            github_put_file('users.json', users, sha)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user_data['id'],
                'username': session['username'],
                'first_name': session['first_name'],
                'last_name': session['last_name']
            }
        })
    except Exception as e:
        print(f"Auth error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/check', methods=['GET'])
def auth_check():
    """Check if user is authenticated"""
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session['user_id'],
                'username': session['username']
            }
        })
    return jsonify({'authenticated': False})

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True})

# ==================== TRANSLATIONS ====================

@app.route('/api/translations/<lang>', methods=['GET'])
def get_translations(lang):
    """Get translations for specified language"""
    if lang not in TRANSLATIONS:
        lang = 'en'
    return jsonify(TRANSLATIONS[lang])

# ==================== BANK API ====================

@app.route('/api/bank/users', methods=['GET'])
@require_auth
def get_bank_users():
    """Get all bank users"""
    users, _ = github_get_file('bank_users.json')
    return jsonify(users or [])

@app.route('/api/bank/my-account', methods=['GET'])
@require_auth
def get_my_bank_account():
    """Get current user's bank account"""
    users, _ = github_get_file('bank_users.json')
    if not users:
        return jsonify({'success': False, 'error': 'No users found'}), 404
    
    user = next((u for u in users if u.get('telegram_id') == session['user_id']), None)
    if not user:
        # Create account for user
        users_data, sha = github_get_file('users.json')
        user_data = next((u for u in users_data if u['telegram_id'] == session['user_id']), None)
        
        new_account = {
            'telegram_id': session['user_id'],
            'username': session['username'],
            'balance': 1000,  # Starting balance
            'isAdmin': False,
            'online': True,
            'deleted': False
        }
        users.append(new_account)
        github_put_file('bank_users.json', users)
        return jsonify(new_account)
    
    return jsonify(user)

@app.route('/api/bank/transfer', methods=['POST'])
@require_auth
def bank_transfer():
    """Make a bank transfer"""
    data = request.json
    to_username = data.get('to')
    amount = float(data.get('amount', 0))
    comment = data.get('comment', '')
    
    if amount <= 0:
        return jsonify({'success': False, 'error': 'Invalid amount'}), 400
    
    users, sha = github_get_file('bank_users.json')
    if not users:
        return jsonify({'success': False, 'error': 'No users found'}), 404
    
    from_user = next((u for u in users if u.get('telegram_id') == session['user_id']), None)
    to_user = next((u for u in users if u['username'] == to_username and not u.get('deleted')), None)
    
    if not from_user or not to_user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    if from_user['balance'] < amount:
        return jsonify({'success': False, 'error': 'Insufficient funds'}), 400
    
    # Update balances
    from_user['balance'] -= amount
    to_user['balance'] += amount
    github_put_file('bank_users.json', users, sha)
    
    # Add to history
    history, h_sha = github_get_file('bank_history.json')
    if history is None:
        history = []
    
    history.insert(0, {
        'time': datetime.now().isoformat(),
        'from': from_user['username'],
        'to': to_user['username'],
        'amount': amount,
        'comment': comment,
        'type': 'transfer'
    })
    github_put_file('bank_history.json', history, h_sha)
    
    return jsonify({'success': True, 'balance': from_user['balance']})

@app.route('/api/bank/history', methods=['GET'])
@require_auth
def get_bank_history():
    """Get bank transaction history"""
    history, _ = github_get_file('bank_history.json')
    if not history:
        return jsonify([])
    
    # Filter to show only current user's transactions
    my_username = session['username']
    my_history = [h for h in history if h['from'] == my_username or h['to'] == my_username]
    
    return jsonify(my_history[:100])  # Last 100 transactions

# ==================== SHOP API ====================

@app.route('/api/shop/products', methods=['GET'])
def get_shop_products():
    """Get all shop products"""
    products, _ = github_get_file('shop_products.json')
    return jsonify(products or [])

@app.route('/api/shop/my-store', methods=['GET'])
@require_auth
def get_my_store():
    """Get current user's store"""
    stores, _ = github_get_file('shop_stores.json')
    if not stores:
        return jsonify(None)
    
    store = next((s for s in stores if s['owner_telegram_id'] == session['user_id']), None)
    return jsonify(store)

@app.route('/api/shop/purchase', methods=['POST'])
@require_auth
def shop_purchase():
    """Purchase products from shop"""
    data = request.json
    cart = data.get('cart', [])
    
    if not cart:
        return jsonify({'success': False, 'error': 'Empty cart'}), 400
    
    # Calculate total
    products, p_sha = github_get_file('shop_products.json')
    total = 0
    for item in cart:
        product = next((p for p in products if p['id'] == item['id']), None)
        if not product or product['stock'] < item['qty']:
            return jsonify({'success': False, 'error': 'Product unavailable'}), 400
        total += product['price'] * item['qty']
    
    # Check bank balance
    users, u_sha = github_get_file('bank_users.json')
    user = next((u for u in users if u.get('telegram_id') == session['user_id']), None)
    
    if not user or user['balance'] < total:
        return jsonify({'success': False, 'error': 'Insufficient funds'}), 400
    
    # Update inventory and balances
    for item in cart:
        product = next((p for p in products if p['id'] == item['id']), None)
        product['stock'] -= item['qty']
        product['soldCount'] = product.get('soldCount', 0) + item['qty']
    
    user['balance'] -= total
    
    github_put_file('shop_products.json', products, p_sha)
    github_put_file('bank_users.json', users, u_sha)
    
    return jsonify({'success': True, 'balance': user['balance']})

# ==================== MYWORK API ====================

@app.route('/api/mywork/start-shift', methods=['POST'])
@require_auth
def start_shift():
    """Start a work shift"""
    running, sha = github_get_file('mywork_running.json')
    if running is None:
        running = {}
    
    username = session['username']
    if username in running:
        return jsonify({'success': False, 'error': 'Shift already started'}), 400
    
    running[username] = datetime.now().isoformat()
    github_put_file('mywork_running.json', running, sha)
    
    return jsonify({'success': True})

@app.route('/api/mywork/stop-shift', methods=['POST'])
@require_auth
def stop_shift():
    """Stop a work shift"""
    data = request.json
    minutes = data.get('minutes', 0)
    pay = data.get('pay', 0)
    
    running, r_sha = github_get_file('mywork_running.json')
    username = session['username']
    
    if not running or username not in running:
        return jsonify({'success': False, 'error': 'No active shift'}), 400
    
    start_time = running.pop(username)
    github_put_file('mywork_running.json', running, r_sha)
    
    # Save shift
    shifts, s_sha = github_get_file('mywork_shifts.json')
    if shifts is None:
        shifts = {}
    
    if username not in shifts:
        shifts[username] = []
    
    shifts[username].insert(0, {
        'start': start_time,
        'end': datetime.now().isoformat(),
        'minutes': minutes,
        'pay': pay
    })
    
    github_put_file('mywork_shifts.json', shifts, s_sha)
    
    return jsonify({'success': True})

@app.route('/api/mywork/shifts', methods=['GET'])
@require_auth
def get_shifts():
    """Get user's shift history"""
    shifts, _ = github_get_file('mywork_shifts.json')
    if not shifts:
        return jsonify([])
    
    username = session['username']
    return jsonify(shifts.get(username, []))

# ==================== MYINFO API ====================

@app.route('/api/myinfo/records', methods=['GET'])
@require_auth
def get_myinfo_records():
    """Get user's info records"""
    records, _ = github_get_file('myinfo_records.json')
    if not records:
        return jsonify({})
    
    username = session['username']
    return jsonify(records.get(username, {}))

@app.route('/api/myinfo/records', methods=['POST'])
@require_auth
def save_myinfo_records():
    """Save user's info records"""
    data = request.json
    
    records, sha = github_get_file('myinfo_records.json')
    if records is None:
        records = {}
    
    username = session['username']
    records[username] = data
    
    github_put_file('myinfo_records.json', records, sha)
    
    return jsonify({'success': True})

# ==================== HEALTH & INIT ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'github_configured': GITHUB_TOKEN != 'YOUR_GITHUB_TOKEN_HERE',
        'bot_configured': BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE'
    })

@app.route('/api/init', methods=['POST'])
def initialize_storage():
    """Initialize GitHub storage with default data"""
    try:
        # Initialize bank users
        github_put_file('bank_users.json', [])
        github_put_file('bank_history.json', [])
        
        # Initialize shop
        github_put_file('shop_products.json', [
            {'id': 1, 'title': 'Смартфон', 'description': 'Современный смартфон', 'price': 2500, 'stock': 5, 'category': 'electronics', 'icon': '📱', 'soldCount': 0},
            {'id': 2, 'title': 'Ноутбук', 'description': 'Мощный ноутбук', 'price': 5000, 'stock': 3, 'category': 'electronics', 'icon': '💻', 'soldCount': 0},
        ])
        github_put_file('shop_stores.json', [])
        
        # Initialize mywork
        github_put_file('mywork_shifts.json', {})
        github_put_file('mywork_running.json', {})
        
        # Initialize myinfo
        github_put_file('myinfo_records.json', {})
        
        # Initialize users
        github_put_file('users.json', [])
        
        return jsonify({'success': True, 'message': 'Storage initialized'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    # Check GitHub configuration
    if GITHUB_TOKEN == 'YOUR_GITHUB_TOKEN_HERE':
        print("❌ ERROR: Set GITHUB_TOKEN environment variable")
        print("export GITHUB_TOKEN='your_token'")
        print("export GITHUB_REPO='username/repository'")
        exit(1)
    
    print("🚀 HomeOS Multi-User Server v2")
    print(f"📦 GitHub Repo: {GITHUB_REPO}")
    print(f"🌿 Branch: {GITHUB_BRANCH}")
    
    # Check BOT_TOKEN (warning only, not fatal)
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("⚠️  WARNING: BOT_TOKEN not set!")
        print("   Telegram authentication will not work.")
        print("   Get token from @BotFather and add to .env file")
        print("")
        print("   For now, you can:")
        print("   - Test API endpoints manually")
        print("   - Initialize GitHub storage")
        print("   - Set up BOT_TOKEN later")
        print("")
    else:
        print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
    
    print("✅ Server running on http://0.0.0.0:5000")
    print("📖 Health check: http://localhost:5000/api/health")
    print("🔧 Initialize storage: curl -X POST http://localhost:5000/api/init")
    print("")
    print("Press Ctrl+C to stop")
    print("")
    
    app.run(host='0.0.0.0', port=5000, debug=True)