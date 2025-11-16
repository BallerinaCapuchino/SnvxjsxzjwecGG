#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HomeOS Setup and Verification Script
Проверяет все зависимости и настройки
"""

import sys
import os
import subprocess
import json

# Fix Windows encoding issues
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def check_python_version():
    """Check Python version"""
    print("[*] Проверка версии Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[ERR] Python {version.major}.{version.minor} слишком старый")
        print("   Требуется Python 3.8 или выше")
        return False

def check_env_file():
    """Check .env file exists and is configured"""
    print("\n[*] Проверка .env файла...")
    
    if not os.path.exists('.env'):
        print("[ERR] Файл .env не найден")
        print("   Создаю из .env.example...")
        
        if os.path.exists('.env.example'):
            with open('.env.example', 'r', encoding='utf-8') as f:
                content = f.read()
            with open('.env', 'w', encoding='utf-8') as f:
                f.write(content)
            print("[OK] Файл .env создан")
            print("[!] ВАЖНО: Отредактируйте .env и добавьте ваши токены!")
            return False
        else:
            print("[ERR] .env.example не найден")
            return False
    
    # Read .env and check configuration
    with open('.env', 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    config = {}
    for line in env_content.split('\n'):
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            config[key.strip()] = value.strip()
    
    print("[OK] Файл .env существует")
    
    # Check GITHUB_TOKEN
    github_token = config.get('GITHUB_TOKEN', '')
    if github_token and github_token != 'YOUR_GITHUB_TOKEN_HERE' and github_token != 'your_github_personal_access_token':
        print(f"[OK] GITHUB_TOKEN: настроен ({github_token[:20]}...)")
    else:
        print("[ERR] GITHUB_TOKEN не настроен в .env")
        return False
    
    # Check GITHUB_REPO
    github_repo = config.get('GITHUB_REPO', '')
    if github_repo and github_repo != 'username/repository':
        print(f"[OK] GITHUB_REPO: {github_repo}")
    else:
        print("[ERR] GITHUB_REPO не настроен в .env")
        return False
    
    # Check BOT_TOKEN (warning only)
    bot_token = config.get('BOT_TOKEN', '')
    if bot_token and bot_token != 'YOUR_BOT_TOKEN_HERE' and bot_token != 'ваш_токен_бота_от_BotFather':
        print(f"[OK] BOT_TOKEN: настроен ({bot_token[:15]}...)")
    else:
        print("[!] BOT_TOKEN не настроен (можно добавить позже)")
    
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n[*] Проверка зависимостей...")
    
    required = ['flask', 'flask_cors', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"[OK] {package}")
        except ImportError:
            print(f"[ERR] {package} не установлен")
            missing.append(package)
    
    if missing:
        print("\n[*] Установка недостающих пакетов...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_v2.txt'])
            print("[OK] Все пакеты установлены")
            return True
        except subprocess.CalledProcessError:
            print("[ERR] Ошибка установки пакетов")
            return False
    
    return True

def check_github_connection():
    """Test GitHub API connection"""
    print("\n[*] Проверка подключения к GitHub...")
    
    try:
        import requests
        
        # Read config from .env
        config = {}
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        
        github_token = config.get('GITHUB_TOKEN', '')
        github_repo = config.get('GITHUB_REPO', '')
        
        if not github_token or not github_repo:
            print("[ERR] GitHub не настроен в .env")
            return False
        
        # Test API
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(
            f'https://api.github.com/repos/{github_repo}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            repo_data = response.json()
            print(f"[OK] Подключение к GitHub успешно")
            print(f"   Репозиторий: {repo_data['full_name']}")
            print(f"   Приватный: {repo_data['private']}")
            return True
        elif response.status_code == 401:
            print("[ERR] GitHub токен недействителен")
            print("   Проверьте GITHUB_TOKEN в .env")
            return False
        elif response.status_code == 404:
            print("[ERR] Репозиторий не найден")
            print(f"   Проверьте GITHUB_REPO в .env: {github_repo}")
            return False
        else:
            print(f"[ERR] Ошибка GitHub API: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERR] Ошибка проверки GitHub: {e}")
        return False

def create_data_folder():
    """Ensure data folder exists in GitHub repo"""
    print("\n[*] Проверка папки data/ в репозитории...")
    
    try:
        import requests
        
        # Read config
        config = {}
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        
        github_token = config.get('GITHUB_TOKEN', '')
        github_repo = config.get('GITHUB_REPO', '')
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Check if data folder exists
        response = requests.get(
            f'https://api.github.com/repos/{github_repo}/contents/data',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("[OK] Папка data/ существует")
            return True
        elif response.status_code == 404:
            print("[!] Папка data/ не найдена")
            print("\n[*] Создайте папку data/ в репозитории:")
            print("   1. Откройте https://github.com/" + github_repo)
            print("   2. Нажмите 'Add file' → 'Create new file'")
            print("   3. Введите имя: data/.gitkeep")
            print("   4. Нажмите 'Commit changes'")
            return False
        else:
            print(f"[!] Не удалось проверить папку data/: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[!] Ошибка проверки папки data/: {e}")
        return False

def main():
    """Run setup checks"""
    print("=" * 60)
    print("HomeOS Multi-User Setup")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Environment File", check_env_file),
        ("Dependencies", check_dependencies),
        ("GitHub Connection", check_github_connection),
        ("Data Folder", create_data_folder),
    ]
    
    all_passed = True
    
    for name, check_func in checks:
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("[SUCCESS] Всё готово к запуску!")
        print("=" * 60)
        print()
        print("\nСледующие шаги:")
        print()
        print("1. Запустите сервер:")
        print("   python server_v2.py")
        print()
        print("2. В новом терминале инициализируйте хранилище:")
        print("   curl -X POST http://localhost:5000/api/init")
        print("   или: python test_server.py")
        print()
        print("3. Проверьте что данные появились в GitHub:")
        print(f"   https://github.com/{os.getenv('GITHUB_REPO', 'username/repo')}/tree/main/data")
        print()
        print("4. (Опционально) Получите BOT_TOKEN от @BotFather")
        print("   и добавьте в .env для Telegram аутентификации")
        print()
        return 0
    else:
        print("[ERROR] Найдены проблемы при настройке")
        print("=" * 60)
        print()
        print("Исправьте ошибки выше и запустите снова:")
        print("   python setup.py")
        print()
        return 1

if __name__ == '__main__':
    sys.exit(main())