# 🚀 Bot Xususiyatlari (Features)

Bot uchun barcha mavjud funksiyalar va ulardan foydalanish yo'riqnomasi.

---

## 1️⃣ Multimodal AI Chat

### Matn Suhbatlari
```
Siz: Python haqida gapirib ber
Bot: [Batafsil Python haqida ma'lumot]
```

### Rasm Tahlili
```
1. Rasmni yuboring
2. Caption qo'shing (ixtiyoriy): "Bu rasmda nima bor?"
3. Bot avtomatik tahlil qiladi
```

### PDF Hujjatlar
```
1. PDF faylni yuklang
2. Caption: "Bu hujjatni xulosala"
3. Bot mazmunni o'qiydi va javob beradi
```

---

## 2️⃣ Tarjima (Translation)

### Oddiy Tarjima
```
Siz: Translate to English: Men dasturchi
Bot: I am a programmer
```

### Qo'llab-quvvatlanadigan Tillar
- 🇺🇿 O'zbek (uz)
- 🇷🇺 Русский (ru)
- 🇬🇧 English (en)
- 🇹🇷 Türkçe (tr)
- 🇩🇪 Deutsch (de)
- 🇫🇷 Français (fr)
- 🇪🇸 Español (es)
- 🇨🇳 中文 (zh)
- 🇯🇵 日本語 (ja)
- 🇰🇷 한국어 (ko)

---

## 3️⃣ Xulosalash (Summarization)

### Qisqa Xulosa
```
Siz: Summarize: [uzun matn]
Bot: [2-3 jumlada xulosa]
```

### Asosiy Fikrlar
```
Siz: Key points: [matn]
Bot:
• Birinchi muhim fikr
• Ikkinchi muhim fikr
• ...
```

### TL;DR
```
Siz: TL;DR: [juda uzun matn]
Bot: [1 jumlada xulosa]
```

---

## 4️⃣ YouTube Tahlili

### Video Haqida Ma'lumot
```
Siz: Analyze video: https://youtube.com/watch?v=...
Bot: [Video haqida ma'lumot va tavsiya]
```

### Content Ideas
```
Siz: Suggest content about: AI va Machine Learning
Bot: [5 ta video g'oyasi]
```

---

## 5️⃣ Ovoz va Audio

### Ovozli Xabar
```
1. Ovozli xabar yuboring
2. Bot ovozni matnga o'giradi
3. Matn bo'yicha javob beradi
```

### Audio Fayl
```
1. Audio fayl yuklang (MP3, OGG, etc.)
2. Bot transkripsiya qiladi
3. Til va davomiylik ko'rsatiladi
```

---

## 6️⃣ RAG Knowledge Base

### Hujjat Qo'shish
```
1. PDF yuboring
2. "Add to knowledge base" ni tanlang
3. Hujjat saqlandi!
```

### Hujjatlardan Savol
```
Siz: Ask from my documents: Python'da decoratorlar qanday ishlaydi?
Bot: [Sizning hujjatlaringiz asosida javob]

📚 Manbalar: Python_Advanced.pdf
```

### Hujjatlar Ro'yxati
```
/mydocs - Barcha hujjatlaringizni ko'rish
```

---

## 7️⃣ Sozlamalar (Settings)

### Til Tanlash
```
/settings → 🌐 Til
- O'zbek
- Русский  
- English
```

### AI Personality
```
/settings → 🤖 AI Shaxsiyati
- 🎩 Rasmiy (formal)
- 😊 Do'stona (friendly)
- 🤓 Professional
- 😄 Kulgili (funny)
```

### Javob Uzunligi
```
/settings → 📏 Javob uzunligi
- 📝 Qisqa (2-3 jumla)
- 📄 O'rtacha (5-7 jumla)
- 📚 Batafsil (to'liq javob)
```

---

## 8️⃣ Bookmarks (Favorites)

### Xabarni Saqlash
```
Bot javobiga reply qiling:
/save programming_tips

Yoki:
/save - default tag bilan saqlash
```

### Saqlangan Xabarlar
```
/bookmarks - Barcha saqlangan xabarlar
```

### Tag Bo'yicha Qidirish
```
/bookmarks programming_tips
```

---

## 9️⃣ Export & Import

### Suhbatni Export Qilish
```
/export → Format tanlang:
- 📄 PDF (chiroyli format)
- 📋 JSON (ma'lumotlar)
- 📝 TXT (oddiy matn)
```

### Import
```
1. JSON fayl yuboring
2. Bot avtomatik import qiladi
3. Eski suhbatlar tiklanadi
```

---

## 🔟 Statistika va Analytics

### Shaxsiy Statistika
```
/stats

📊 Statistika:
• Sizning xabarlaringiz: 145
• Rasmlar: 23
• Hujjatlar: 5
• Ovozli: 12
• Jami foydalanuvchilar: 1,234
```

### Grafik Ko'rinish
```
Admin panel orqali:
/admin → 📊 Statistika
```

---

## 1️⃣1️⃣ Admin Panel (Faqat Adminlar)

### Foydalanuvchilar
```
/admin → 👥 Foydalanuvchilar
- Jami foydalanuvchilar
- Faol foydalanuvchilar
- Statistika
```

### Broadcasting
```
/admin → 📢 Broadcast
1. Xabar yozing
2. Barcha foydalanuvchilarga yuboriladi
3. Progress tracking
```

### Logs va Monitoring
```
/admin → 🗂 Loglar
- Real-time logs
- Error tracking
- System status
```

---

## 1️⃣2️⃣ Advanced Features

### Caching
- Tez-tez so'ralgan savollar cache'dan
- Tarjimalar cache'lanadi
- User preferences cache'da
- Redis yoki in-memory

### Rate Limiting
- API limitlarni boshqarish
- Fair usage policy
- Premium users uchun unlimited

### Multi-step Conversations
- Form to'ldirish
- Step-by-step yo'riqnomalar
- Context awareness

---

## 💡 Maslahatlar (Tips)

### 1. Tez Javob Olish
```
- Qisqa savollar bering
- Response length: "Qisqa" ni tanlang
- Cache ishlatiladi
```

### 2. Yaxshi Natijalar
```
- Aniq savol bering
- Kontekst qo'shing
- Misol ko'rsating
```

### 3. RAG Dan Foydalanish
```
- Hujjatlarni oldindan yuklab qo'ying
- Tag qo'shing (masalan: "python", "tutorial")
- Aniq savol bering
```

### 4. Xotira Tozalash
```
- Vaqti-vaqti bilan /clear bajaring
- Export qilib, keyin clear qiling
- Eski bookmarks'ni o'chiring
```

---

## 🆘 Yordam

### Savol-Javob

**Q: Bot sekin javob beryapti?**
A: Response length'ni "Qisqa"ga o'zgartiring yoki cache clear qiling.

**Q: RAG ishlamayapti?**
A: Avval hujjat yuklang va "Add to knowledge base" ni tanlang.

**Q: Export ishlamayapti?**
A: PDF uchun reportlab o'rnatilgan bo'lishi kerak.

**Q: Admin panel ochilmayapti?**
A: `.env` faylda `ADMIN_IDS` ni to'g'ri sozlang.

---

## 🚀 Keyingi Yangilanishlar

Rejada:
- [ ] Voice generation (TTS)
- [ ] Image generation (DALL-E)
- [ ] Video analysis from file
- [ ] Multi-user conversations
- [ ] Plugins system

---

**Savollar?** /help yuboring yoki admin bilan bog'laning!
