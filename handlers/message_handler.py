"""
Message handler for text and media messages (images, documents).
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from services import GeminiService
from database import ChatHistoryDB

router = Router()

# Initialize services
gemini_service = GeminiService()
db = ChatHistoryDB()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command."""
    await message.answer(
        "🤖 Salom! Men Gemini AI botman.\n\n"
        "Men quyidagilarni qila olaman:\n"
        "📝 Matn xabarlarga javob berish\n"
        "🖼 Rasmlarni tahlil qilish\n"
        "📄 PDF hujjatlarni o'qish\n"
        "🎤 Ovozli xabarlarni tushunish\n\n"
        "Kommandalar:\n"
        "/clear - Suhbat tarixini tozalash\n"
        "/stats - Statistikani ko'rish"
    )


@router.message(Command("clear"))
async def cmd_clear(message: Message):
    """Clear chat history for user."""
    user_id = message.from_user.id
    db.clear_history(user_id)
    await message.answer("✅ Suhbat tarixi tozalandi!")


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Show user statistics."""
    user_id = message.from_user.id
    message_count = db.get_message_count(user_id)
    total_users = db.get_user_count()
    
    await message.answer(
        f"📊 Statistika:\n\n"
        f"Sizning xabarlaringiz: {message_count}\n"
        f"Jami foydalanuvchilar: {total_users}"
    )


@router.message(F.text & ~F.text.startswith('/'))
async def handle_text_message(message: Message):
    """Handle regular text messages."""
    user_id = message.from_user.id
    user_text = message.text
    
    # Send typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Get chat history
        history = db.get_history(user_id)
        
        # Save user message
        db.add_message(user_id, "user", user_text, "text")
        
        # Generate response
        response = await gemini_service.generate_response(
            prompt=user_text,
            history=history
        )
        
        # Save AI response
        db.add_message(user_id, "model", response, "text")
        
        # Send response
        await message.answer(response)
        
    except Exception as e:
        error_msg = f"Xatolik yuz berdi: {str(e)}"
        print(f"❌ {error_msg}")
        await message.answer(f"❌ {error_msg}")


@router.message(F.photo)
async def handle_photo(message: Message):
    """Handle photo messages."""
    user_id = message.from_user.id
    
    # Send typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Get the largest photo
        photo = message.photo[-1]
        
        # Download photo
        photo_file = await message.bot.get_file(photo.file_id)
        photo_data = await message.bot.download_file(photo_file.file_path)
        image_bytes = photo_data.read()
        
        # Get caption or use default prompt
        caption = message.caption or "Bu rasmda nima ko'rsatilgan? Batafsil tahlil qiling."
        
        # Get chat history
        history = db.get_history(user_id)
        
        # Save user message
        db.add_message(user_id, "user", f"[RASM] {caption}", "image")
        
        # Analyze image
        response = await gemini_service.generate_response(
            prompt=caption,
            history=history,
            image_data=image_bytes
        )
        
        # Save AI response
        db.add_message(user_id, "model", response, "text")
        
        # Send response
        await message.answer(f"🖼 Rasm tahlili:\n\n{response}")
        
    except Exception as e:
        error_msg = f"Rasmni qayta ishlashda xatolik: {str(e)}"
        print(f"❌ {error_msg}")
        await message.answer(f"❌ {error_msg}")


@router.message(F.document)
async def handle_document(message: Message):
    """Handle document messages (PDF, etc.)."""
    user_id = message.from_user.id
    document = message.document
    
    # Send typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Check if it's a PDF
        if document.mime_type == "application/pdf":
            # Download document
            doc_file = await message.bot.get_file(document.file_id)
            doc_data = await message.bot.download_file(doc_file.file_path)
            doc_bytes = doc_data.read()
            
            # Get caption or use default prompt
            caption = message.caption or "Bu PDF hujjatni tahlil qiling va mazmunini tushuntiring."
            
            # Get chat history
            history = db.get_history(user_id)
            
            # Save user message
            db.add_message(user_id, "user", f"[PDF: {document.file_name}] {caption}", "document")
            
            # Analyze document
            response = await gemini_service.analyze_document(
                document_data=doc_bytes,
                prompt=caption,
                mime_type=document.mime_type
            )
            
            # Save AI response
            db.add_message(user_id, "model", response, "text")
            
            # Send response
            await message.answer(f"📄 Hujjat tahlili ({document.file_name}):\n\n{response}")
        else:
            await message.answer(
                "⚠️ Hozircha faqat PDF hujjatlarni tahlil qila olaman.\n"
                f"Sizning fayl turi: {document.mime_type}"
            )
    
    except Exception as e:
        error_msg = f"Hujjatni qayta ishlashda xatolik: {str(e)}"
        print(f"❌ {error_msg}")
        await message.answer(f"❌ {error_msg}")
