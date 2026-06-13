@echo off
chcp 65001 > nul

echo 🤖 Telegram Gemini Bot - O'rnatish boshlandi...
echo.

REM Check Python
echo 📋 Python versiyasini tekshirish...
python --version
if errorlevel 1 (
    echo ❌ Python topilmadi! Iltimos, Python 3.10+ o'rnating.
    pause
    exit /b 1
)
echo ✅ Python topildi
echo.

REM Create virtual environment
echo 📦 Virtual environment yaratilmoqda...
python -m venv venv
if errorlevel 1 (
    echo ❌ Virtual environment yaratishda xatolik!
    pause
    exit /b 1
)
echo ✅ Virtual environment yaratildi
echo.

REM Activate virtual environment
echo 🔄 Virtual environment faollashtirish...
call venv\Scripts\activate.bat
echo ✅ Virtual environment faollashtirildi
echo.

REM Upgrade pip
echo ⬆️  pip yangilanmoqda...
python -m pip install --upgrade pip --quiet
echo ✅ pip yangilandi
echo.

REM Install requirements
echo 📥 Kutubxonalar o'rnatilmoqda...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ❌ Kutubxonalarni o'rnatishda xatolik!
    pause
    exit /b 1
)
echo ✅ Barcha kutubxonalar o'rnatildi
echo.

REM Create .env file
if not exist .env (
    echo 📝 .env fayl yaratilmoqda...
    copy .env.example .env
    echo ✅ .env fayl yaratildi
    echo.
    echo ⚠️  MUHIM: .env faylini tahrirlang va API kalitlarini kiriting:
    echo    - TELEGRAM_BOT_TOKEN
    echo    - GEMINI_API_KEY
    echo    - GROQ_API_KEY
) else (
    echo ✅ .env fayl mavjud
)

echo.
echo ✨ O'rnatish muvaffaqiyatli yakunlandi!
echo.
echo 📌 Keyingi qadamlar:
echo    1. .env faylini tahrirlang: notepad .env
echo    2. Virtual environment'ni faollashtiring: venv\Scripts\activate
echo    3. Botni ishga tushiring: python main.py
echo.
pause
