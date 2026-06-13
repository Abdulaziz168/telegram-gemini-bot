# ⚡ Tez Boshlash (Quick Start)

## 5 daqiqada botni ishga tushiring! 🚀

### 1️⃣ API Kalitlarni tayyorlang

Quyidagi 3 ta API kalitni oling:

#### 🤖 Telegram Bot Token
1. Telegram'da [@BotFather](https://t.me/BotFather) ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomini kiriting (masalan: "Mening AI Botim")
4. Username kiriting (masalan: "my_ai_bot")
5. Token'ni nusxalab oling

#### 🧠 Gemini API Key
1. [Google AI Studio](https://makersuite.google.com/app/apikey) ga kiring
2. "Get API key" tugmasini bosing
3. Kalitni nusxalab oling

#### 🎤 Groq API Key
1. [Groq Console](https://console.groq.com/) ga kiring
2. Ro'yxatdan o'ting (GitHub bilan)
3. "API Keys" → "Create API Key" bosing
4. Kalitni nusxalab oling

---

### 2️⃣ Botni o'rnating

#### Windows uchun:
```bash
# 1. Papkaga kiring
cd telegram-gemini-bot

# 2. Setup scriptni ishga tushiring
setup.bat

# 3. .env faylini tahrirlang
notepad .env
```

#### Linux/Mac uchun:
```bash
# 1. Papkaga kiring
cd telegram-gemini-bot

# 2. Setup scriptni ishga tushiring
chmod +x setup.sh
./setup.sh

# 3. .env faylini tahrirlang
nano .env
```

---

### 3️⃣ .env faylini to'ldiring

`.env` faylini oching va quyidagilarni kiriting:

```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
GEMINI_API_KEY=AIzaSyB_your_key_here
GROQ_API_KEY=gsk_your_key_here
```

**Muhim:** Haqiqiy kalitlarni kiriting! Yuqoridagi misollar ishlamaydi.

---

### 4️⃣ Botni ishga tushiring

#### Windows:
```bash
# Virtual environment'ni faollashtiring
venv\Scripts\activate

# Botni ishga tushiring
python main.py
```

#### Linux/Mac:
```bash
# Virtual environment'ni faollashtiring
source venv/bin/activate

# Botni ishga tushiring
python main.py
```

Agar hammasi to'g'ri bo'lsa, siz quyidagilarni ko'rasiz:
```
✅ Konfiguratsiya tekshirildi
✅ Ma'lumotlar bazasi tayyor
✅ Bot tayyor: @your_bot_username
📡 Polling boshlanmoqda...
```

---

### 5️⃣ Botni sinab ko'ring!

1. Telegram'da o'z botingizni toping
2. `/start` buyrug'ini yuboring
3. Savol bering: "Salom, qalaysan?"
4. Rasm yuboring
5. Ovozli xabar yuboring

**Tabriklaymiz! 🎉** Botingiz ishlayapti!

---

## 🆘 Muammo yuzaga kelsa?

### ❌ "Module not found" xatosi
```bash
pip install -r requirements.txt
```

### ❌ "Invalid token" xatosi
- `.env` fayldagi `TELEGRAM_BOT_TOKEN` ni tekshiring
- Token to'liq nusxalanganligiga ishonch hosil qiling

### ❌ "Gemini API error"
- Gemini API keyingiz to'g'riligini tekshiring
- Internet aloqangizni tekshiring
- [Google AI Studio](https://makersuite.google.com/app/apikey) da API key'ni qayta yarating

### ❌ "Groq API error"
- Groq API keyingiz to'g'riligini tekshiring
- Daily limit'ga yetmaganligingizni tekshiring
- [Groq Console](https://console.groq.com/) da API key'ni qayta yarating

### ❌ Virtual environment ishlamayapti
**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📚 Keyingi qadamlar

Botni sozlash va kengaytirish uchun quyidagi fayllarni o'qing:

- 📖 [README.md](README.md) - To'liq dokumentatsiya
- 📊 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Kod strukturasi
- ⚙️ [config.py](config.py) - Sozlamalar

---

## 💡 Maslahatlar

### Botni serverda ishlatish
```bash
# Screen yoki tmux ishlatish (Linux)
screen -S telegram_bot
python main.py
# Ctrl+A, D - detach qilish

# Qayta ulanish
screen -r telegram_bot
```

### Log faylga yozish
```bash
python main.py > bot.log 2>&1 &
```

### Chat tarixini ko'rish
```bash
sqlite3 chat_history.db
SELECT * FROM chat_history LIMIT 10;
.quit
```

---

## 🎯 Botning imkoniyatlari

| Xususiyat | Misol |
|-----------|-------|
| **Matn** | "Python haqida gapirib ber" |
| **Rasm** | Rasm + "Bu rasmda nima bor?" |
| **PDF** | PDF fayl + "Mazmunini aytib ber" |
| **Ovoz** | Ovozli xabar yuboring |
| **Tarix** | `/clear` - tarixni tozalash |
| **Statistika** | `/stats` - ma'lumotlar |

---

**Savollar?** Issue oching yoki botga `/start` yuboring!

**Muammo?** README.md'dagi "Debug" bo'limiga qarang!

**Yordam kerak?** Telegram: [@your_support_username]

---

Omad! Botingizdan bahramand bo'ling! 🚀
