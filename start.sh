#!/bin/bash

# HomeOS Quick Start Script

echo "🏠 HomeOS Multi-User Server - Quick Start"
echo "=========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env file with your tokens"
    exit 1
fi

# Check if BOT_TOKEN is set
if grep -q "YOUR_BOT_TOKEN_HERE" .env; then
    echo "⚠️  BOT_TOKEN not configured!"
    echo ""
    echo "Чтобы получить токен бота:"
    echo "1. Откройте Telegram и найдите @BotFather"
    echo "2. Отправьте команду /newbot"
    echo "3. Следуйте инструкциям для создания бота"
    echo "4. Скопируйте токен и добавьте в .env файл"
    echo ""
    echo "После этого запустите скрипт снова"
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check if requirements are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip3 install -r requirements_v2.txt
fi

echo "✅ Dependencies OK"
echo ""

# Check if data folder exists in GitHub repo
echo "🔍 Checking GitHub repository..."
GITHUB_TOKEN=$(grep GITHUB_TOKEN .env | cut -d '=' -f2)
GITHUB_REPO=$(grep GITHUB_REPO .env | cut -d '=' -f2)

# Test GitHub connection
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$GITHUB_REPO")

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ GitHub connection OK"
else
    echo "❌ Cannot connect to GitHub repository"
    echo "HTTP Code: $HTTP_CODE"
    echo "Please check your GITHUB_TOKEN and GITHUB_REPO in .env"
    exit 1
fi

echo ""
echo "🚀 Starting server..."
echo ""

# Start server
python3 server_v2.py