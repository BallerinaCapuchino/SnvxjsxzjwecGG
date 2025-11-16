#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Синхронизация локальных данных с GitHub репозиторием
"""
import os
import sys
import subprocess
import shutil
import json
from datetime import datetime

# Fix Windows encoding
if os.name == 'nt':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

DATA_DIR = 'server_data'
REPO_DIR = 'homeos_data_repo'

def run_command(cmd, cwd=None):
    """Выполнить команду"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            shell=True,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, '', str(e)

def setup_git_repo():
    """Настроить локальный git репозиторий"""
    
    # Читаем конфигурацию
    config = {}
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()
    
    github_repo = config.get('GITHUB_REPO', '')
    if not github_repo:
        print("[ERR] GITHUB_REPO не настроен в .env")
        return False
    
    # Проверяем существует ли репозиторий
    if os.path.exists(REPO_DIR):
        print(f"[OK] Репозиторий {REPO_DIR} уже существует")
        return True
    
    print(f"[*] Клонирование репозитория {github_repo}...")
    
    # Клонируем репозиторий
    success, stdout, stderr = run_command(
        f'git clone https://github.com/{github_repo}.git {REPO_DIR}'
    )
    
    if success:
        print("[OK] Репозиторий склонирован")
        return True
    else:
        print(f"[ERR] Ошибка клонирования: {stderr}")
        return False

def sync_data():
    """Синхронизировать данные с GitHub"""
    
    if not os.path.exists(REPO_DIR):
        if not setup_git_repo():
            return False
    
    # Создаем папку data если её нет
    data_folder = os.path.join(REPO_DIR, 'data')
    os.makedirs(data_folder, exist_ok=True)
    
    # Копируем все JSON файлы
    if not os.path.exists(DATA_DIR):
        print(f"[ERR] Папка {DATA_DIR} не найдена")
        return False
    
    print("[*] Копирование данных...")
    
    copied = 0
    for filename in os.listdir(DATA_DIR):
        if filename.endswith('.json'):
            src = os.path.join(DATA_DIR, filename)
            dst = os.path.join(data_folder, filename)
            shutil.copy2(src, dst)
            print(f"    Скопирован: {filename}")
            copied += 1
    
    if copied == 0:
        print("[!] Нет данных для синхронизации")
        return False
    
    print(f"[OK] Скопировано {copied} файлов")
    
    # Git add
    print("[*] Добавление изменений в git...")
    success, _, _ = run_command('git add data/', cwd=REPO_DIR)
    
    if not success:
        print("[ERR] Ошибка git add")
        return False
    
    # Git commit
    commit_msg = f"Update data - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    success, stdout, stderr = run_command(
        f'git commit -m "{commit_msg}"',
        cwd=REPO_DIR
    )
    
    if 'nothing to commit' in stdout or 'nothing to commit' in stderr:
        print("[OK] Нет изменений для коммита")
        return True
    
    if not success and 'nothing to commit' not in stderr:
        print(f"[ERR] Ошибка git commit: {stderr}")
        return False
    
    print("[OK] Изменения закоммичены")
    
    # Git push
    print("[*] Отправка в GitHub...")
    success, stdout, stderr = run_command('git push', cwd=REPO_DIR)
    
    if success:
        # Читаем конфигурацию для вывода URL
        config = {}
        if os.path.exists('.env'):
            with open('.env', 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        
        print("[OK] Данные успешно отправлены в GitHub!")
        print(f"    https://github.com/{config.get('GITHUB_REPO', '')}/tree/main/data")
        return True
    else:
        print(f"[ERR] Ошибка git push: {stderr}")
        print("")
        print("Возможные причины:")
        print("1. Нет прав доступа - настройте SSH ключ или токен")
        print("2. Нужно выполнить: cd {REPO_DIR} && git remote set-url origin https://YOUR_TOKEN@github.com/{config.get('GITHUB_REPO', '')}.git")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("HomeOS - Синхронизация данных с GitHub")
    print("=" * 60)
    print("")
    
    if sync_data():
        print("")
        print("=" * 60)
        print("[SUCCESS] Синхронизация завершена!")
        print("=" * 60)
        return 0
    else:
        print("")
        print("=" * 60)
        print("[ERROR] Ошибка синхронизации")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())