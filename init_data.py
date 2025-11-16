#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Инициализация данных для HomeOS сервера
"""
import requests
import sys

print("[*] Инициализация данных HomeOS...")

try:
    response = requests.post('http://localhost:5000/api/init')
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("[OK] Данные успешно инициализированы!")
            print(f"[*] Расположение: {data.get('location')}")
            print("")
            print("Теперь вы можете:")
            print("1. Открыть index.html в браузере")
            print("2. Или настроить Telegram Web App")
        else:
            print(f"[ERR] Ошибка: {data.get('error')}")
            sys.exit(1)
    else:
        print(f"[ERR] Ошибка HTTP: {response.status_code}")
        print(f"      {response.text}")
        sys.exit(1)
        
except requests.exceptions.ConnectionError:
    print("[ERR] Не удается подключиться к серверу")
    print("      Убедитесь что сервер запущен: python server_simple.py")
    sys.exit(1)
except Exception as e:
    print(f"[ERR] Ошибка: {e}")
    sys.exit(1)