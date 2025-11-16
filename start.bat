@echo off
REM HomeOS Quick Start Script for Windows

echo ========================================
echo 🏠 HomeOS Multi-User Server - Quick Start
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found!
    echo Creating from .env.example...
    copy .env.example .env
    echo ✅ Please edit .env file with your tokens
    pause
    exit /b 1
)

REM Check if BOT_TOKEN is set
findstr /C:"YOUR_BOT_TOKEN_HERE" .env >nul
if %errorlevel% equ 0 (
    echo ⚠️  BOT_TOKEN not configured!
    echo.
    echo Чтобы получить токен бота:
    echo 1. Откройте Telegram и найдите @BotFather
    echo 2. Отправьте команду /newbot
    echo 3. Следуйте инструкциям для создания бота
    echo 4. Скопируйте токен и добавьте в .env файл
    echo.
    echo После этого запустите скрипт снова
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo Please install Python 3.11 or higher from python.org
    pause
    exit /b 1
)

REM Check if requirements are installed
echo 📦 Checking dependencies...
python -c "import flask" 2>nul
if %errorlevel% neq 0 (
    echo 📥 Installing dependencies...
    pip install -r requirements_v2.txt
)

echo ✅ Dependencies OK
echo.

echo 🚀 Starting server...
echo.
echo Server will be available at: http://localhost:5000
echo Press Ctrl+C to stop
echo.

REM Start server
python server_v2.py

pause