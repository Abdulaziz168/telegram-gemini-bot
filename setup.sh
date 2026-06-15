#!/bin/bash

# Telegram Bot Setup Script

echo "🤖 Telegram Gemini Bot - O'rnatish boshlandi..."
echo ""

# Check Python version
echo "📋 Python versiyasini tekshirish..."
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
echo "✅ Python $python_version topildi"
echo ""

# Create virtual environment
echo "📦 Virtual environment yaratilmoqda..."
python3 -m venv venv
echo "✅ Virtual environment yaratildi"
echo ""

# Activate virtual environment
echo "🔄 Virtual environment faollashtirish..."
source venv/bin/activate
echo "✅ Virtual environment faollashtirildi"
echo ""

# Upgrade pip
echo "⬆️  pip yangilanmoqda..."
pip install --upgrade pip --quiet
echo "✅ pip yangilandi"
echo ""

# Install requirements
echo "📥 Kutubxonalar o'rnatilmoqda..."
pip install -r requirements.txt --quiet
echo "✅ Barcha kutubxonalar o'rnatildi"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 .env fayl yaratilmoqda..."
    cp .env.example .env
    echo "✅ .env fayl yaratildi"
    echo ""
    echo "⚠️  MUHIM: .env faylini tahrirlang va API kalitlarini kiriting:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - GEMINI_API_KEY"
    echo "   - GROQ_API_KEY"
else
    echo "✅ .env fayl mavjud"
fi

echo ""
echo "✨ O'rnatish muvaffaqiyatli yakunlandi!"
echo ""
echo "📌 Keyingi qadamlar:"
echo "   1. .env faylini tahrirlang: nano .env"
echo "   2. Virtual environment'ni faollashtiring: source venv/bin/activate"
echo "   3. Botni ishga tushiring: python main.py"
echo ""
