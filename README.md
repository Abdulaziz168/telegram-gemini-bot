# 🤖 Telegram Bot: Multimodal Gemini + Groq STT

Ko'p funksiyali Telegram bot - matn, rasm, hujjat va ovozli xabarlar bilan ishlaydi. Google Gemini 1.5 Flash va Groq Whisper-large-v3 asosida qurilgan.

## ✨ Imkoniyatlari

- 💬 **Matn suhbatlari** - Gemini AI bilan suhbatlashish
- 🖼️ **Rasm tahlili** - Rasmlarni ko'rish va tahlil qilish (Vision)
- 📄 **PDF hujjatlar** - PDF fayllarni o'qish va tahlil qilish
- 🎤 **Ovozli xabarlar** - Ovozni matnga aylantirish (STT) va javob berish
- 💾 **Suhbat tarixi** - Har bir foydalanuvchi uchun kontekstni saqlash
- 📊 **Statistika** - Foydalanish statistikasini ko'rish

## 🏗️ Arxitektura

```
telegram-gemini-bot/
├── main.py                 # Bot ishga tushirish nuqtasi
├── config.py               # Konfiguratsiya va environment variables
├── requirements.txt        # Python kutubxonalari
├── .env.example           # Environment variables namunasi
├── services/              # AI xizmatlari
│   ├── __init__.py
│   ├── gemini.py          # Google Gemini multimodal AI
│   └── groq_stt.py        # Groq Whisper STT
├── handlers/              # Telegram message handlers
│   ├── __init__.py
│   ├── message_handler.py # Matn va media handlerlari
│   └── voice_handler.py   # Ovozli xabar handlerlari
└── database/              # Ma'lumotlar bazasi
    ├── __init__.py
    └── chat_history.py    # SQLite chat history
```

## 🚀 O'rnatish

### 1. Repository'ni klonlash

```bash
git clone <repository-url>
cd telegram-gemini-bot
```

### 2. Virtual environment yaratish

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate     # Windows
```

### 3. Kutubxonalarni o'rnatish

```bash
pip install -r requirements.txt
```

### 4. Environment variables sozlash

`.env` fayl yarating va quyidagi ma'lumotlarni kiriting:

```bash
cp .env.example .env
```

`.env` faylini tahrirlang:

```env
# Telegram Bot Token (@BotFather dan oling)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Google Gemini API Key (https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key_here

# Groq API Key (https://console.groq.com/)
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Botni ishga tushirish

```bash
python main.py
```

## 📋 API Kalitlarini olish

### Telegram Bot Token
1. [@BotFather](https://t.me/BotFather) ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot uchun nom va username tanlang
4. Token'ni nusxalab oling

### Google Gemini API Key
1. [Google AI Studio](https://makersuite.google.com/app/apikey) ga kiring
2. "Get API key" tugmasini bosing
3. API kalitni nusxalab oling

### Groq API Key
1. [Groq Console](https://console.groq.com/) ga kiring
2. "API Keys" bo'limiga o'ting
3. "Create API Key" tugmasini bosing
4. API kalitni nusxalab oling

## 🎯 Foydalanish

### Komandalar

- `/start` - Botni ishga tushirish va yordam
- `/clear` - Suhbat tarixini tozalash
- `/stats` - Statistikani ko'rish

### Qo'llab-quvvatlanadigan xabar turlari

1. **Matn** - Oddiy matn xabarlarini yuboring
2. **Rasm** - Rasm yuboring (caption qo'shishingiz mumkin)
3. **PDF** - PDF hujjat yuboring (caption qo'shishingiz mumkin)
4. **Ovoz** - Ovozli xabar yuboring (avtomatik transkripsiya)
5. **Audio** - Audio fayl yuboring (transkripsiya bilan)

## 🛠️ Texnologiyalar

- **Python 3.10+**
- **aiogram 3.x** - Telegram Bot framework
- **google-generativeai** - Gemini AI SDK
- **groq** - Groq API (Whisper STT)
- **Pillow** - Rasm qayta ishlash
- **SQLite** - Chat history saqlash

## 📊 Ma'lumotlar bazasi

Bot SQLite dan foydalanib, har bir foydalanuvchi uchun suhbat tarixini saqlaydi:

```sql
CREATE TABLE chat_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    role TEXT,              -- 'user' yoki 'model'
    content TEXT,
    timestamp DATETIME,
    message_type TEXT       -- 'text', 'image', 'document', 'voice'
);
```

## 🔒 Xavfsizlik

- ✅ Environment variables `.env` faylida saqlanadi
- ✅ `.env` fayli `.gitignore` ga qo'shilgan
- ✅ API kalitlari kodga yozilmagan
- ✅ Gemini safety settings faollashtirilgan

## 🐛 Debug

Agar muammo yuzaga kelsa:

```bash
# Loglarni ko'rish
python main.py

# Virtual environment to'g'ri faollashganini tekshiring
which python  # Linux/Mac
where python  # Windows

# Kutubxonalarni qayta o'rnatish
pip install --force-reinstall -r requirements.txt
```

## 📝 Eslatmalar

- Gemini API bepul, lekin limit mavjud
- Groq API juda tez, lekin daily limit bor
- Katta fayllar uchun Telegram file size limiti 20 MB
- PDF tahlili uchun Gemini 1.5 Flash yetarli tez va sifatli

## 🤝 Hissa qo'shish

Pull requestlar qabul qilinadi! Katta o'zgarishlar uchun avval issue oching.

## 📄 Litsenziya

MIT License

## 👨‍💻 Muallif

Kiro AI tomonidan yaratilgan

---

**Savol va takliflar uchun:** [Issue oching](../../issues)

**Yordam kerakmi?** Botga `/start` yuboring!
