"""
Feature handlers: Translation, Summarization, YouTube, RAG, Export, Settings.
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from services.translation import TranslationService
from services.summarizer import SummarizerService
from services.youtube import YouTubeService
from services.rag import RAGService
from database import ChatHistoryDB
from database.user_preferences import UserPreferencesDB
from utils.keyboards import KeyboardBuilder
from utils.states import UserStates
from utils.export import ExportService

router = Router()

# Initialize services
translation_service = TranslationService()
summarizer_service = SummarizerService()
youtube_service = YouTubeService()
rag_service = RAGService()
db = ChatHistoryDB()
prefs_db = UserPreferencesDB()
export_service = ExportService()


# ==================== TRANSLATION ====================

@router.message(Command("translate"))
async def cmd_translate(message: Message, state: FSMContext):
    """Start translation flow."""
    await message.answer(
        "🌐 <b>Tarjima</b>\n\n"
        "Tarjima qilmoqchi bo'lgan matnni yuboring:",
    )
    await state.set_state(UserStates.waiting_for_translation_text)


@router.message(UserStates.waiting_for_translation_text)
async def receive_translation_text(message: Message, state: FSMContext):
    """Receive text to translate and ask for target language."""
    await state.update_data(translation_text=message.text)
    await message.answer(
        "🌐 Qaysi tilga tarjima qilish kerak?",
        reply_markup=KeyboardBuilder.translation_menu()
    )
    await state.set_state(UserStates.waiting_for_translation_target)


@router.callback_query(F.data.startswith("translate_"), UserStates.waiting_for_translation_target)
async def process_translation(callback: CallbackQuery, state: FSMContext):
    """Process translation with selected language."""
    target_lang = callback.data.replace("translate_", "")
    data = await state.get_data()
    text = data.get("translation_text", "")

    await callback.message.edit_text("⏳ Tarjima qilinmoqda...")

    result = await translation_service.translate(text, target_lang)

    lang_flags = {"uz": "🇺🇿", "ru": "🇷🇺", "en": "🇬🇧", "tr": "🇹🇷", "de": "🇩🇪", "fr": "🇫🇷"}
    flag = lang_flags.get(target_lang, "🌐")

    await callback.message.edit_text(
        f"{flag} <b>Tarjima:</b>\n\n{result}"
    )
    await state.clear()
    await callback.answer()


# ==================== SUMMARIZATION ====================

@router.message(Command("summarize"))
async def cmd_summarize(message: Message, state: FSMContext):
    """Start summarization flow."""
    await message.answer(
        "📝 <b>Xulosa</b>\n\n"
        "Xulosalash kerak bo'lgan matnni yuboring:"
    )
    await state.set_state(UserStates.waiting_for_summary_text)


@router.message(UserStates.waiting_for_summary_text)
async def receive_summary_text(message: Message, state: FSMContext):
    """Receive text and show summary options."""
    await state.update_data(summary_text=message.text)
    await message.answer(
        "📝 Xulosa turini tanlang:",
        reply_markup=KeyboardBuilder.summarize_menu()
    )
    await state.set_state(UserStates.waiting_for_summary_options)


@router.callback_query(F.data.startswith("summary_"), UserStates.waiting_for_summary_options)
async def process_summary(callback: CallbackQuery, state: FSMContext):
    """Process summarization with selected option."""
    option = callback.data.replace("summary_", "")
    data = await state.get_data()
    text = data.get("summary_text", "")

    await callback.message.edit_text("⏳ Xulosalanmoqda...")

    if option == "keypoints":
        result = await summarizer_service.summarize_key_points(text)
    elif option == "tldr":
        result = await summarizer_service.tldr(text)
    else:
        result = await summarizer_service.summarize(text, max_length=option)

    await callback.message.edit_text(
        f"📝 <b>Xulosa:</b>\n\n{result}"
    )
    await state.clear()
    await callback.answer()


# ==================== YOUTUBE ====================

@router.message(Command("youtube"))
async def cmd_youtube(message: Message):
    """Handle YouTube command."""
    args = message.text.replace("/youtube", "").strip()
    if not args:
        await message.answer(
            "🎬 <b>YouTube Tahlil</b>\n\n"
            "Foydalanish:\n"
            "• <code>/youtube [URL]</code> — video tahlili\n"
            "• <code>/youtube_ideas [mavzu]</code> — kontent g'oyalari"
        )
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    result = await youtube_service.analyze_video_description(args)
    await message.answer(f"🎬 <b>YouTube Tahlil:</b>\n\n{result}")


@router.message(Command("youtube_ideas"))
async def cmd_youtube_ideas(message: Message):
    """Generate YouTube content ideas."""
    topic = message.text.replace("/youtube_ideas", "").strip()
    if not topic:
        await message.answer("💡 Mavzuni kiriting: <code>/youtube_ideas [mavzu]</code>")
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    result = await youtube_service.suggest_content(topic)
    await message.answer(f"💡 <b>Kontent G'oyalari:</b>\n\n{result}")


# ==================== RAG (Knowledge Base) ====================

@router.message(Command("knowledge"))
async def cmd_knowledge(message: Message):
    """Show knowledge base info."""
    user_id = message.from_user.id
    docs = rag_service.get_user_documents(user_id)
    doc_count = rag_service.get_document_count(user_id)

    text = (
        "📚 <b>Bilimlar Bazasi (RAG)</b>\n\n"
        f"Sizning hujjatlaringiz: {doc_count} ta\n\n"
        "Buyruqlar:\n"
        "• <code>/ask [savol]</code> — bazadan savol so'rash\n"
        "• <code>/add_doc [sarlavha]</code> — hujjat qo'shish\n"
        "• <code>/my_docs</code> — hujjatlaringiz ro'yxati\n\n"
    )

    if docs:
        text += "<b>Oxirgi hujjatlar:</b>\n"
        for doc in docs[:5]:
            text += f"• {doc['title']} ({doc['created_at'][:10]})\n"

    await message.answer(text)


@router.message(Command("ask"))
async def cmd_ask_knowledge(message: Message):
    """Ask question from knowledge base."""
    question = message.text.replace("/ask", "").strip()
    if not question:
        await message.answer("❓ Savolingizni kiriting: <code>/ask [savol]</code>")
        return

    await message.bot.send_chat_action(message.chat.id, "typing")

    user_id = message.from_user.id
    result = await rag_service.ask_with_context(question, user_id)
    await message.answer(f"📚 <b>Javob:</b>\n\n{result}")


@router.message(Command("add_doc"))
async def cmd_add_doc(message: Message, state: FSMContext):
    """Add document to knowledge base."""
    title = message.text.replace("/add_doc", "").strip()
    if not title:
        await message.answer(
            "📄 Hujjat sarlavhasini kiriting:\n"
            "<code>/add_doc [sarlavha]</code>\n\n"
            "Keyin matn yuboring."
        )
        return

    await state.update_data(doc_title=title)
    await message.answer(
        f"📄 Sarlavha: <b>{title}</b>\n\n"
        "Endi hujjat matnini yuboring:"
    )
    await state.set_state(UserStates.idle)  # We'll handle with a special flag


@router.message(Command("my_docs"))
async def cmd_my_docs(message: Message):
    """List user's documents."""
    user_id = message.from_user.id
    docs = rag_service.get_user_documents(user_id)

    if not docs:
        await message.answer("📂 Sizda hali hujjatlar yo'q.\n<code>/add_doc [sarlavha]</code> bilan qo'shing.")
        return

    text = "📂 <b>Sizning hujjatlaringiz:</b>\n\n"
    for i, doc in enumerate(docs, 1):
        text += f"{i}. {doc['title']}"
        if doc.get('source'):
            text += f" ({doc['source']})"
        text += f"\n   📅 {doc['created_at'][:10]}\n"

    await message.answer(text)


# ==================== EXPORT ====================

@router.message(Command("export"))
async def cmd_export(message: Message, state: FSMContext):
    """Export chat history."""
    await message.answer(
        "📥 <b>Suhbat tarixini eksport qilish</b>\n\n"
        "Formatni tanlang:",
        reply_markup=KeyboardBuilder.export_menu()
    )
    await state.set_state(UserStates.choosing_export_format)


@router.callback_query(F.data.startswith("export_"), UserStates.choosing_export_format)
async def process_export(callback: CallbackQuery, state: FSMContext):
    """Process export with selected format."""
    export_format = callback.data.replace("export_", "")
    user_id = callback.from_user.id

    await callback.message.edit_text("⏳ Eksport qilinmoqda...")

    # Get chat history
    history = db.get_history(user_id, limit=100)

    if not history:
        await callback.message.edit_text("📂 Suhbat tarixi bo'sh.")
        await state.clear()
        await callback.answer()
        return

    try:
        if export_format == "json":
            file_data = export_service.export_to_json(history, user_id)
            filename = f"chat_history_{user_id}.json"
        elif export_format == "txt":
            file_data = export_service.export_to_txt(history, user_id)
            filename = f"chat_history_{user_id}.txt"
        elif export_format == "pdf":
            file_data = export_service.export_to_pdf(history, user_id)
            filename = f"chat_history_{user_id}.pdf"
        else:
            await callback.message.edit_text("❌ Noto'g'ri format.")
            await state.clear()
            return

        document = BufferedInputFile(
            file=file_data.getvalue(),
            filename=filename
        )

        await callback.message.delete()
        await callback.message.answer_document(
            document=document,
            caption=f"📥 Suhbat tarixi ({export_format.upper()} format)"
        )
    except Exception as e:
        await callback.message.edit_text(f"❌ Eksport xatosi: {str(e)}")

    await state.clear()
    await callback.answer()


# ==================== SETTINGS ====================

@router.message(Command("settings"))
async def cmd_settings(message: Message):
    """Show settings menu."""
    await message.answer(
        "⚙️ <b>Sozlamalar</b>\n\n"
        "Quyidagi sozlamalarni o'zgartirishingiz mumkin:",
        reply_markup=KeyboardBuilder.settings_menu()
    )


@router.callback_query(F.data == "settings_language")
async def settings_language(callback: CallbackQuery):
    """Language settings."""
    await callback.message.edit_text(
        "🌐 <b>Til tanlang:</b>",
        reply_markup=KeyboardBuilder.language_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lang_"))
async def set_language(callback: CallbackQuery):
    """Set user language."""
    lang = callback.data.replace("lang_", "")
    user_id = callback.from_user.id

    prefs_db.set_preference(user_id, "language", lang)

    lang_names = {"uz": "🇺🇿 O'zbek", "ru": "🇷🇺 Русский", "en": "🇬🇧 English"}
    await callback.message.edit_text(
        f"✅ Til o'zgartirildi: {lang_names.get(lang, lang)}"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_personality")
async def settings_personality(callback: CallbackQuery):
    """AI personality settings."""
    await callback.message.edit_text(
        "🤖 <b>AI Shaxsiyatini tanlang:</b>",
        reply_markup=KeyboardBuilder.personality_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("personality_"))
async def set_personality(callback: CallbackQuery):
    """Set AI personality."""
    personality = callback.data.replace("personality_", "")
    user_id = callback.from_user.id

    prefs_db.set_preference(user_id, "ai_personality", personality)

    names = {
        "formal": "🎩 Rasmiy",
        "friendly": "😊 Do'stona",
        "professional": "🤓 Professional",
        "funny": "😄 Kulgili"
    }
    await callback.message.edit_text(
        f"✅ AI shaxsiyati o'zgartirildi: {names.get(personality, personality)}"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_length")
async def settings_length(callback: CallbackQuery):
    """Response length settings."""
    await callback.message.edit_text(
        "📏 <b>Javob uzunligini tanlang:</b>",
        reply_markup=KeyboardBuilder.response_length_menu()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("length_"))
async def set_length(callback: CallbackQuery):
    """Set response length."""
    length = callback.data.replace("length_", "")
    user_id = callback.from_user.id

    prefs_db.set_preference(user_id, "response_length", length)

    names = {"short": "📝 Qisqa", "medium": "📄 O'rtacha", "long": "📚 Batafsil"}
    await callback.message.edit_text(
        f"✅ Javob uzunligi o'zgartirildi: {names.get(length, length)}"
    )
    await callback.answer()


@router.callback_query(F.data == "settings_clear")
async def settings_clear(callback: CallbackQuery):
    """Clear history confirmation."""
    await callback.message.edit_text(
        "⚠️ Suhbat tarixini tozalashni xohlaysizmi?",
        reply_markup=KeyboardBuilder.confirm_action("clear_history")
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_clear_history")
async def confirm_clear(callback: CallbackQuery):
    """Confirm clearing history."""
    user_id = callback.from_user.id
    db.clear_history(user_id)
    await callback.message.edit_text("✅ Suhbat tarixi tozalandi!")
    await callback.answer()


@router.callback_query(F.data == "cancel_clear_history")
async def cancel_clear(callback: CallbackQuery):
    """Cancel clearing history."""
    await callback.message.edit_text("❌ Bekor qilindi.")
    await callback.answer()


@router.callback_query(F.data == "settings_export")
async def settings_export(callback: CallbackQuery, state: FSMContext):
    """Export from settings."""
    await callback.message.edit_text(
        "📥 Eksport formatini tanlang:",
        reply_markup=KeyboardBuilder.export_menu()
    )
    await state.set_state(UserStates.choosing_export_format)
    await callback.answer()


@router.callback_query(F.data == "settings_favorites")
async def settings_favorites(callback: CallbackQuery):
    """Show bookmarks/favorites."""
    user_id = callback.from_user.id
    bookmarks = prefs_db.get_bookmarks(user_id)

    if not bookmarks:
        await callback.message.edit_text(
            "⭐ <b>Saqlangan xabarlar</b>\n\n"
            "Hali hech narsa saqlanmagan.\n"
            "<code>/bookmark [matn]</code> bilan saqlang."
        )
    else:
        text = "⭐ <b>Saqlangan xabarlar:</b>\n\n"
        for i, bm in enumerate(bookmarks, 1):
            msg = bm['message'][:100] + "..." if len(bm['message']) > 100 else bm['message']
            text += f"{i}. {msg}\n"
            if bm.get('tags'):
                text += f"   🏷 {bm['tags']}\n"
            text += "\n"
        await callback.message.edit_text(text)

    await callback.answer()


@router.callback_query(F.data == "back_settings")
async def back_to_settings(callback: CallbackQuery):
    """Go back to settings menu."""
    await callback.message.edit_text(
        "⚙️ <b>Sozlamalar</b>\n\n"
        "Quyidagi sozlamalarni o'zgartirishingiz mumkin:",
        reply_markup=KeyboardBuilder.settings_menu()
    )
    await callback.answer()


@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    """Go back to main menu."""
    await callback.message.edit_text(
        "🏠 Bosh menyu\n\n"
        "Buyruqlar ro'yxati: /help"
    )
    await callback.answer()


# ==================== BOOKMARKS ====================

@router.message(Command("bookmark"))
async def cmd_bookmark(message: Message):
    """Save a bookmark."""
    text = message.text.replace("/bookmark", "").strip()
    if not text:
        await message.answer(
            "⭐ Saqlash uchun matn kiriting:\n"
            "<code>/bookmark [matn]</code>"
        )
        return

    user_id = message.from_user.id
    prefs_db.add_bookmark(user_id, text)
    await message.answer("⭐ Saqlandi!")


@router.message(Command("bookmarks"))
async def cmd_bookmarks(message: Message):
    """Show all bookmarks."""
    user_id = message.from_user.id
    bookmarks = prefs_db.get_bookmarks(user_id)

    if not bookmarks:
        await message.answer("📂 Saqlangan xabarlar yo'q.")
        return

    text = "⭐ <b>Saqlangan xabarlar:</b>\n\n"
    for i, bm in enumerate(bookmarks, 1):
        msg = bm['message'][:100] + "..." if len(bm['message']) > 100 else bm['message']
        text += f"{i}. {msg}\n"
        if bm.get('tags'):
            text += f"   🏷 {bm['tags']}\n"
        text += "\n"

    await message.answer(text)


# ==================== HELP ====================

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show all available commands."""
    await message.answer(
        "📖 <b>Barcha buyruqlar:</b>\n\n"
        "<b>💬 Asosiy:</b>\n"
        "/start — Botni boshlash\n"
        "/clear — Suhbat tarixini tozalash\n"
        "/stats — Statistika\n"
        "/help — Yordam\n\n"
        "<b>🌐 Tarjima:</b>\n"
        "/translate — Matn tarjimasi\n\n"
        "<b>📝 Xulosa:</b>\n"
        "/summarize — Matnni xulosalash\n\n"
        "<b>🎬 YouTube:</b>\n"
        "/youtube [URL] — Video tahlili\n"
        "/youtube_ideas [mavzu] — Kontent g'oyalari\n\n"
        "<b>📚 Bilimlar Bazasi:</b>\n"
        "/knowledge — Baza haqida\n"
        "/ask [savol] — Bazadan so'rash\n"
        "/add_doc [sarlavha] — Hujjat qo'shish\n"
        "/my_docs — Hujjatlar ro'yxati\n\n"
        "<b>📥 Eksport:</b>\n"
        "/export — Tarixni eksport qilish\n\n"
        "<b>⭐ Saqlash:</b>\n"
        "/bookmark [matn] — Xabar saqlash\n"
        "/bookmarks — Saqlangan xabarlar\n\n"
        "<b>⚙️ Sozlamalar:</b>\n"
        "/settings — Bot sozlamalari\n\n"
        "<b>👨‍💼 Admin:</b>\n"
        "/admin — Admin panel\n\n"
        "<b>🎨 Qo'shimcha:</b>\n"
        "• Rasm yuboring — tahlil qiladi\n"
        "• PDF yuboring — o'qiydi\n"
        "• Ovozli xabar — matnga aylantiradi\n"
        "• Oddiy matn — AI javob beradi"
    )
