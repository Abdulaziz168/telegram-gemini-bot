"""
Voice message handler for speech-to-text conversion.
"""
from aiogram import Router, F
from aiogram.types import Message
from services import GroqSTTService, GeminiService
from database import ChatHistoryDB

router = Router()

# Initialize services
stt_service = GroqSTTService()
gemini_service = GeminiService()
db = ChatHistoryDB()


@router.message(F.voice)
async def handle_voice(message: Message):
    """Handle voice messages."""
    user_id = message.from_user.id
    
    # Send typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Download voice file
        voice_file = await message.bot.get_file(message.voice.file_id)
        voice_data = await message.bot.download_file(voice_file.file_path)
        audio_bytes = voice_data.read()
        
        # Transcribe audio to text
        await message.answer("🎤 Ovozli xabar qabul qilindi, qayta ishlanmoqda...")
        
        transcribed_text = await stt_service.transcribe_audio(
            audio_data=audio_bytes,
            filename="voice.ogg"
        )
        
        if not transcribed_text or transcribed_text.startswith("Ovozni matnga"):
            await message.answer("❌ Ovozni tanib olishda xatolik yuz berdi.")
            return
        
        # Show transcription
        await message.answer(f"📝 Matn: {transcribed_text}")
        
        # Get chat history
        history = db.get_history(user_id)
        
        # Save user message (transcribed)
        db.add_message(user_id, "user", transcribed_text, "voice")
        
        # Generate AI response
        response = await gemini_service.generate_response(
            prompt=transcribed_text,
            history=history
        )
        
        # Save AI response
        db.add_message(user_id, "model", response, "text")
        
        # Send response
        await message.answer(f"🤖 Javob:\n\n{response}")
        
    except Exception as e:
        error_msg = f"Ovozli xabarni qayta ishlashda xatolik: {str(e)}"
        print(f"❌ {error_msg}")
        await message.answer(f"❌ {error_msg}")


@router.message(F.audio)
async def handle_audio(message: Message):
    """Handle audio files."""
    user_id = message.from_user.id
    
    # Send typing indicator
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        audio = message.audio
        
        # Download audio file
        audio_file = await message.bot.get_file(audio.file_id)
        audio_data = await message.bot.download_file(audio_file.file_path)
        audio_bytes = audio_data.read()
        
        await message.answer(f"🎵 Audio fayl qabul qilindi ({audio.file_name}), qayta ishlanmoqda...")
        
        # Get file extension from filename or mime_type
        filename = audio.file_name or "audio.mp3"
        
        # Transcribe with metadata
        result = await stt_service.transcribe_with_metadata(
            audio_data=audio_bytes,
            filename=filename
        )
        
        transcribed_text = result.get("text", "")
        language = result.get("language", "unknown")
        duration = result.get("duration")
        
        if not transcribed_text or "Xatolik" in transcribed_text:
            await message.answer("❌ Audio faylni transkripsiya qilishda xatolik.")
            return
        
        # Show transcription with metadata
        info = f"📝 Transkripsiya:\n{transcribed_text}\n\n"
        info += f"🌐 Til: {language}"
        if duration:
            info += f"\n⏱ Davomiyligi: {duration:.1f} soniya"
        
        await message.answer(info)
        
        # Get chat history
        history = db.get_history(user_id)
        
        # Save user message
        db.add_message(user_id, "user", f"[AUDIO] {transcribed_text}", "voice")
        
        # Generate AI response
        response = await gemini_service.generate_response(
            prompt=transcribed_text,
            history=history
        )
        
        # Save AI response
        db.add_message(user_id, "model", response, "text")
        
        # Send response
        await message.answer(f"🤖 Javob:\n\n{response}")
        
    except Exception as e:
        error_msg = f"Audio faylni qayta ishlashda xatolik: {str(e)}"
        print(f"❌ {error_msg}")
        await message.answer(f"❌ {error_msg}")


@router.message(F.video_note)
async def handle_video_note(message: Message):
    """Handle video notes (round videos)."""
    await message.answer(
        "🎥 Video xabarlar hozircha qo'llab-quvvatlanmaydi.\n"
        "Iltimos, ovozli xabar yoki matn yuboring."
    )
