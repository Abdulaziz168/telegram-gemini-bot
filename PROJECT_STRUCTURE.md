# 📁 Loyiha Strukturasi

## Fayl tizimi

```
telegram-gemini-bot/
│
├── 📄 main.py                     # Bot ishga tushirish (entry point)
├── ⚙️ config.py                   # Konfiguratsiya va env variables
├── 📋 requirements.txt            # Python dependencies
├── 🔒 .env.example                # Environment variables namunasi
├── 📖 README.md                   # Asosiy dokumentatsiya
├── 📊 PROJECT_STRUCTURE.md        # Ushbu fayl
│
├── 🛠️ services/                   # AI xizmatlari
│   ├── __init__.py
│   ├── gemini.py                  # Gemini 1.5 Flash (Multimodal AI)
│   │   └── GeminiService class
│   │       ├── generate_response()      # Chat javoblari
│   │       ├── analyze_image()          # Rasm tahlili
│   │       ├── analyze_document()       # PDF tahlili
│   │       └── escape_markdown()        # Telegram formatting
│   │
│   └── groq_stt.py                # Groq Whisper STT
│       └── GroqSTTService class
│           ├── transcribe_audio()       # Ovozni matnga
│           ├── transcribe_with_metadata() # Metadata bilan
│           └── detect_language()        # Tilni aniqlash
│
├── 🎮 handlers/                   # Telegram message handlers
│   ├── __init__.py
│   ├── message_handler.py         # Matn va media
│   │   └── Handlers:
│   │       ├── /start              # Bot haqida ma'lumot
│   │       ├── /clear              # Tarixni tozalash
│   │       ├── /stats              # Statistika
│   │       ├── text messages       # Oddiy matn
│   │       ├── photos              # Rasm + caption
│   │       └── documents           # PDF fayllar
│   │
│   └── voice_handler.py           # Ovozli xabarlar
│       └── Handlers:
│           ├── voice messages      # Telegram voice
│           ├── audio files         # Audio + metadata
│           └── video notes         # (hozircha qo'llab-quvvatlanmaydi)
│
└── 💾 database/                   # Ma'lumotlar bazasi
    ├── __init__.py
    └── chat_history.py            # SQLite chat history
        └── ChatHistoryDB class
            ├── init_db()               # Jadval yaratish
            ├── add_message()           # Xabar saqlash
            ├── get_history()           # Tarixni olish
            ├── clear_history()         # Tarixni tozalash
            ├── get_user_count()        # Foydalanuvchilar soni
            └── get_message_count()     # Xabarlar soni
```

## 🔄 Data Flow (Ma'lumot oqimi)

### 1️⃣ Matn xabari
```
User → Telegram → main.py → message_handler.py
                               ↓
                        get_history(user_id)
                               ↓
                        gemini.generate_response()
                               ↓
                        add_message() × 2
                               ↓
                        User ← Response
```

### 2️⃣ Rasm tahlili
```
User (Photo) → Telegram → main.py → message_handler.py
                                       ↓
                                download_file()
                                       ↓
                                get_history(user_id)
                                       ↓
                                gemini.generate_response(image_data)
                                       ↓
                                add_message() × 2
                                       ↓
                                User ← Analysis
```

### 3️⃣ Ovozli xabar
```
User (Voice) → Telegram → main.py → voice_handler.py
                                      ↓
                               download_file()
                                      ↓
                               groq_stt.transcribe_audio()
                                      ↓
                               get_history(user_id)
                                      ↓
                               gemini.generate_response(transcription)
                                      ↓
                               add_message() × 2
                                      ↓
                               User ← Transcription + Response
```

### 4️⃣ PDF hujjat
```
User (PDF) → Telegram → main.py → message_handler.py
                                     ↓
                              download_file()
                                     ↓
                              get_history(user_id)
                                     ↓
                              gemini.analyze_document()
                                     ↓
                              add_message() × 2
                                     ↓
                              User ← Document Analysis
```

## 🗄️ Database Schema

### Table: chat_history
```sql
┌──────────────┬──────────────────┬──────────┬─────────┐
│ Column       │ Type             │ Index    │ Purpose │
├──────────────┼──────────────────┼──────────┼─────────┤
│ id           │ INTEGER PRIMARY  │ ✓        │ Unique  │
│ user_id      │ INTEGER NOT NULL │ ✓        │ Telegram│
│ role         │ TEXT NOT NULL    │          │ user/AI │
│ content      │ TEXT NOT NULL    │          │ Message │
│ timestamp    │ DATETIME         │ ✓        │ Time    │
│ message_type │ TEXT             │          │ Type    │
└──────────────┴──────────────────┴──────────┴─────────┘
```

## 🔑 Environment Variables

```env
TELEGRAM_BOT_TOKEN=123456:ABCdefGHI...    # @BotFather
GEMINI_API_KEY=AIzaSyB...                 # Google AI Studio
GROQ_API_KEY=gsk_...                      # Groq Console
DATABASE_PATH=chat_history.db             # (Optional)
MAX_HISTORY_MESSAGES=10                   # (Optional)
```

## 🧩 Dependencies Breakdown

### Core Framework
- `aiogram==3.7.0` - Telegram Bot framework

### AI Services
- `google-generativeai==0.8.3` - Gemini AI SDK
- `groq==0.11.0` - Groq Whisper API

### Utilities
- `Pillow==10.4.0` - Image processing
- `python-dotenv==1.0.1` - Environment variables
- `aiohttp==3.10.5` - Async HTTP client
- `aiofiles==24.1.0` - Async file operations

## 📊 Features Matrix

| Xususiyat          | Status | Handler              | Service           |
|-------------------|--------|---------------------|-------------------|
| Matn suhbati      | ✅     | message_handler.py  | GeminiService     |
| Rasm tahlili      | ✅     | message_handler.py  | GeminiService     |
| PDF tahlili       | ✅     | message_handler.py  | GeminiService     |
| Ovoz → Matn       | ✅     | voice_handler.py    | GroqSTTService    |
| Audio → Matn      | ✅     | voice_handler.py    | GroqSTTService    |
| Chat history      | ✅     | Barcha handlerlar   | ChatHistoryDB     |
| Komandalar        | ✅     | message_handler.py  | -                 |
| Statistika        | ✅     | message_handler.py  | ChatHistoryDB     |

## 🚀 Ishga tushirish

```bash
# 1. Setup
./setup.sh          # Linux/Mac
setup.bat           # Windows

# 2. Configure
nano .env           # API keys

# 3. Run
python main.py
```

## 🎯 Key Classes

### 1. GeminiService
- **Maqsad:** Multimodal AI (text, vision, documents)
- **Model:** gemini-1.5-flash
- **Features:** Chat, image analysis, PDF reading

### 2. GroqSTTService
- **Maqsad:** Speech-to-Text
- **Model:** whisper-large-v3
- **Features:** Fast transcription, language detection

### 3. ChatHistoryDB
- **Maqsad:** SQLite chat history
- **Features:** Per-user context, CRUD operations

## 📝 Notes

- Barcha async/await to'g'ri ishlatilgan
- Error handling har bir handler'da mavjud
- Logging stdout'ga yoziladi
- Database auto-migration (CREATE IF NOT EXISTS)
- Safety settings Gemini'da faollashtirilgan

---

**Yaratildi:** Kiro AI tomonidan
**Versiya:** 1.0.0
**Til:** Python 3.10+
