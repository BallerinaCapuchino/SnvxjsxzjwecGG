#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Автоматическое создание папки data/ в GitHub репозитории
"""

import sys
import os
import requests
import base64

# Fix Windows encoding
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def create_data_folder():
    """Create data folder in GitHub repository"""
    
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
    github_branch = config.get('GITHUB_BRANCH', 'main')
    
    if not github_token or not github_repo:
        print("[ERR] GitHub не настроен в .env")
        return False
    
    print(f"[*] Создание папки data/ в репозитории {github_repo}...")
    
    try:
        # Create .gitkeep file in data folder
        url = f'https://api.github.com/repos/{github_repo}/contents/data/.gitkeep'
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Create empty content
        content = "# This folder stores HomeOS data\n"
        content_encoded = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        payload = {
            'message': 'Create data folder for HomeOS storage',
            'content': content_encoded,
            'branch': github_branch
        }
        
        response = requests.put(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            print("[OK] Папка data/ успешно создана!")
            print(f"    Проверьте: https://github.com/{github_repo}/tree/{github_branch}/data")
            return True
        elif response.status_code == 422:
            # File already exists
            print("[OK] Папка data/ уже существует")
            return True
        else:
            print(f"[ERR] Ошибка создания: {response.status_code}")
            print(f"      {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERR] Ошибка: {e}")
        return False

if __name__ == '__main__':
    success = create_data_folder()
    sys.exit(0 if success else 1)