# 🔧 Muammolarni Hal Qilish (Troubleshooting)

Botda muammo yuzaga kelganda bu qo'llanmadan foydalaning.

---

## 🚨 Umumiy Xatolar

### 1. ❌ "Quyidagi muhim environment variables topilmadi"

**Sabab:** `.env` fayl yo'q yoki bo'sh.

**Yechim:**
```bash
# .env.example dan nusxa oling
cp .env.example .env

# .env faylini tahrirlang
nano .env  # Linux/Mac
notepad .env  # Windows

# Kerakli tokenlarni kiriting
TELEGRAM_BOT_TOKEN=your_token_here
GEMINI_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
```

**Tekshirish:**
```bash
# .env faylini ko'ring
cat .env  # Linux/Mac
type .env  # Windows
```

---

### 2. ❌ "ModuleNotFoundError: No module named 'aiogram'"

**Sabab:** Kutubxonalar o'rnatilmagan.

**Yechim:**
```bash
# Virtual environment faollashtirilganligini tekshiring
which python  # Linux/Mac - venv/bin/python ko'rsatishi kerak
where python  # Windows - venv\Scripts\python ko'rsatishi kerak

# Kutubxonalarni o'rnating
pip install -r requirements.txt

# Agar ishlamasa, qayta o'rnating
pip install --force-reinstall -r requirements.txt
```

---

### 3. ❌ "Unauthorized: Invalid bot token"

**Sabab:** Telegram bot token noto'g'ri.

**Yechim:**
1. [@BotFather](https://t.me/BotFather) ga `/mybots` yuboring
2. O'z botingizni tanlang
3. "API Token" bosing
4. Token'ni to'liq nusxalang (bo'sh joy yo'q!)
5. `.env` fayliga qo'ying:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHI-jklMNOpqrsTUVwxyz
```

**Tekshirish:**
```bash
# Python'da tekshirish
python3 -c "from config import Config; print(Config.TELEGRAM_BOT_TOKEN)"
```

---

### 4. ❌ "Gemini API error: API key not valid"

**Sabab:** Gemini API key noto'g'ri yoki limit tugagan.

**Yechim:**
1. [Google AI Studio](https://makersuite.google.com/app/apikey) ga kiring
2. Yangi API key yarating yoki eskisini ko'ring
3. `.env` ga kiriting:
```env
GEMINI_API_KEY=AIzaSyB_your_actual_key_here
```

**Limit tekshirish:**
- [Quota sahifasi](https://ai.google.dev/pricing) ga tashrif buyuring
- Kunlik limit: 1500 so'rov (bepul)

---

### 5. ❌ "Groq STT xatosi: rate limit exceeded"

**Sabab:** Groq API daily limit'ga yetdingiz.

**Yechim:**
- **Kuting:** 24 soat kuting
- **Yangi key:** [Groq Console](https://console.groq.com/) da yangi akkaunt oching
- **Limit:** Bepul plan: 14,400 so'rov/kun

**Hozirgi limitni tekshirish:**
```bash
curl -X GET "https://api.groq.com/openai/v1/models" \
  -H "Authorization: Bearer $GROQ_API_KEY"
```

---

### 6. ❌ "sqlite3.OperationalError: unable to open database file"

**Sabab:** Database faylini yaratishga ruxsat yo'q.

**Yechim:**
```bash
# Joriy papkada yozish huquqi borligini tekshiring
ls -la  # Linux/Mac
dir  # Windows

# Ruxsat bering
chmod 755 .  # Linux/Mac

# Yoki boshqa joygа ko'rsating
echo "DATABASE_PATH=/tmp/chat_history.db" >> .env
```

---

## 🐛 Debug Mode

### Logging'ni yoqish

`main.py` da logging level'ni o'zgartiring:

```python
logging.basicConfig(
    level=logging.DEBUG,  # INFO dan DEBUG ga o'zgartiring
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Test mode

Botni test qilish uchun:

```python
# config.py da
MAX_HISTORY_MESSAGES = 3  # Kam qilish (test uchun)
```

---

## 🔍 Xatolarni Aniqlash

### 1. Python versiyasini tekshirish
```bash
python --version  # 3.10 yoki yuqori bo'lishi kerak
```

Agar kichik bo'lsa:
```bash
# Linux (Ubuntu/Debian)
sudo apt update
sudo apt install python3.10

# macOS
brew install python@3.10

# Windows - python.org dan yuklab oling
```

### 2. Kutubxona versiyalarini tekshirish
```bash
pip list | grep aiogram
pip list | grep google-generativeai
pip list | grep groq
```

### 3. Internet aloqasini tekshirish
```bash
# Google AI Studio'ga kirish
curl https://generativelanguage.googleapis.com/v1beta/models

# Groq API'ga kirish
curl https://api.groq.com/openai/v1/models
```

### 4. .env faylini tekshirish
```bash
# Bo'sh qatorlar yo'qligini tekshiring
cat .env | grep -v '^$'

# Har bir kalitning borligini tekshiring
grep TELEGRAM_BOT_TOKEN .env
grep GEMINI_API_KEY .env
grep GROQ_API_KEY .env
```

---

## 🏥 Tez Diagnostika

### Bot ishlamayapti?

Quyidagi buyruqlarni ketma-ket bajaring:

```bash
# 1. Virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate      # Windows

# 2. Python versiyasi
python --version

# 3. Kutubxonalar
pip list | grep aiogram

# 4. Config
python -c "from config import Config; Config.validate()"

# 5. Database
python -c "from database import ChatHistoryDB; db = ChatHistoryDB(); print('OK')"

# 6. Gemini
python -c "from services import GeminiService; gs = GeminiService(); print('OK')"

# 7. Groq
python -c "from services import GroqSTTService; ss = GroqSTTService(); print('OK')"
```

Qaysi qadamda xato bo'lsa, shu yerda muammo bor!

---

## 📱 Platform-Specific Issues

### Windows

**Problem:** `'python' is not recognized`
```bash
# PATH'ga qo'shing yoki to'liq yo'l ko'rsating
C:\Python310\python.exe main.py
```

**Problem:** Virtual environment ishlamayapti
```bash
# Execution Policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Linux/Mac

**Problem:** Permission denied
```bash
chmod +x setup.sh
chmod +x main.py
```

**Problem:** Python3 topilmayapti
```bash
sudo apt install python3-pip python3-venv  # Ubuntu/Debian
brew install python3  # macOS
```

---

## 🎯 Performance Issues

### Bot sekin ishlayapti?

1. **Chat history limitini kamaytiring:**
```env
MAX_HISTORY_MESSAGES=5
```

2. **Typing indicator qo'shing** (allaqachon mavjud):
```python
await message.bot.send_chat_action(message.chat.id, "typing")
```

3. **Database indexlarini tekshiring** (allaqachon mavjud):
```sql
CREATE INDEX IF NOT EXISTS idx_user_id ON chat_history(user_id, timestamp);
```

---

## 🆘 Yordam Olish

### 1. Loglarni saqlang
```bash
python main.py > bot.log 2>&1
```

### 2. Error messageni nusxalang
```bash
tail -n 50 bot.log  # Linux/Mac
```

### 3. Versiyalarni yig'ing
```bash
echo "Python: $(python --version)"
echo "aiogram: $(pip show aiogram | grep Version)"
echo "OS: $(uname -a)"  # Linux/Mac
```

### 4. Issue oching
- Repository'da "Issues" → "New Issue"
- Yuqoridagi ma'lumotlarni qo'shing
- Xato haqida batafsil yozing

---

## 📞 Qo'shimcha Resurslar

- **Telegram Bot API:** https://core.telegram.org/bots/api
- **aiogram docs:** https://docs.aiogram.dev/
- **Gemini API:** https://ai.google.dev/docs
- **Groq API:** https://console.groq.com/docs

---

## ✅ Checklist

Botni ishga tushirishdan oldin:

- [ ] Python 3.10+ o'rnatilgan
- [ ] Virtual environment yaratilgan va faollashtirilgan
- [ ] `requirements.txt` o'rnatilgan
- [ ] `.env` fayl mavjud va to'ldirilgan
- [ ] Telegram bot yaratilgan (@BotFather)
- [ ] Gemini API key olingan
- [ ] Groq API key olingan
- [ ] Internet aloqasi ishlayapti
- [ ] Database papkasiga yozish ruxsati bor

Hammasi ✅ bo'lsa, bot ishashi kerak! 🚀

---

Muammo hal bo'lmasa, Issue oching! 💬
