"""
STT (Speech-to-Text) service using Google Gemini.
Gemini handles Uzbek language much better than Whisper.
"""
import google.generativeai as genai
from typing import Optional
import io
from config import Config

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)


class GroqSTTService:
    """Service for converting speech to text using Gemini AI.
    
    Note: Class name kept as GroqSTTService for backward compatibility,
    but now uses Gemini for better Uzbek language recognition.
    """
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        """
        Initialize Gemini STT service.
        
        Args:
            model: Gemini model to use
        """
        self.model = genai.GenerativeModel(model)
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        filename: str = "audio.ogg"
    ) -> str:
        """
        Transcribe audio to text using Gemini.
        
        Args:
            audio_data: Audio file bytes
            language: Optional language code (e.g., 'uz', 'ru', 'en')
            filename: Filename with extension (needed for format detection)
            
        Returns:
            Transcribed text
        """
        try:
            # Determine MIME type from filename
            mime_type = self._get_mime_type(filename)
            
            # Build prompt
            if language == "uz":
                prompt = "Bu audio faylni tinglang va undagi gapni to'liq o'zbek tilida yozing. Faqat matni yozing, boshqa hech narsa qo'shmang."
            elif language == "ru":
                prompt = "Прослушайте это аудио и напишите точный текст на русском языке. Только текст, ничего больше."
            elif language == "en":
                prompt = "Listen to this audio and write the exact text in English. Only the text, nothing else."
            else:
                prompt = (
                    "Bu audio faylni tinglang va undagi gapni aniq yozing. "
                    "Agar o'zbek tilida bo'lsa, o'zbek tilida yozing. "
                    "Agar rus tilida bo'lsa, rus tilida yozing. "
                    "Agar ingliz tilida bo'lsa, ingliz tilida yozing. "
                    "Faqat matni yozing, boshqa hech narsa qo'shmang."
                )
            
            # Upload audio to Gemini
            audio_file = genai.upload_file(
                io.BytesIO(audio_data),
                mime_type=mime_type
            )
            
            # Generate transcription
            response = self.model.generate_content(
                [prompt, audio_file],
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 4096,
                }
            )
            
            # Clean up uploaded file
            try:
                genai.delete_file(audio_file.name)
            except:
                pass
            
            return response.text.strip()
            
        except Exception as e:
            error_msg = f"Gemini STT xatosi: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Ovozni matnga o'girishda xatolik: {str(e)}"
    
    async def transcribe_with_metadata(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        filename: str = "audio.ogg"
    ) -> dict:
        """
        Transcribe audio and return detailed metadata.
        
        Args:
            audio_data: Audio file bytes
            language: Optional language code
            filename: Filename with extension
            
        Returns:
            Dictionary with transcription and metadata
        """
        try:
            mime_type = self._get_mime_type(filename)
            
            prompt = (
                "Bu audio faylni tinglang va quyidagi formatda javob bering:\n"
                "MATN: [audio dagi to'liq matn]\n"
                "TIL: [aniqlangan til kodi, masalan: uz, ru, en]\n\n"
                "Agar o'zbek tilida bo'lsa, o'zbek tilida yozing. "
                "Faqat shu formatda javob bering."
            )
            
            # Upload audio
            audio_file = genai.upload_file(
                io.BytesIO(audio_data),
                mime_type=mime_type
            )
            
            response = self.model.generate_content(
                [prompt, audio_file],
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 4096,
                }
            )
            
            # Clean up
            try:
                genai.delete_file(audio_file.name)
            except:
                pass
            
            # Parse response
            result_text = response.text.strip()
            
            # Try to extract structured data
            text = result_text
            detected_lang = language or "uz"
            
            if "MATN:" in result_text:
                lines = result_text.split("\n")
                for line in lines:
                    if line.startswith("MATN:"):
                        text = line.replace("MATN:", "").strip()
                    elif line.startswith("TIL:"):
                        detected_lang = line.replace("TIL:", "").strip().lower()
            
            return {
                "text": text,
                "language": detected_lang,
                "duration": None,
            }
            
        except Exception as e:
            error_msg = f"Gemini STT metadata xatosi: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "text": f"Xatolik yuz berdi: {str(e)}",
                "language": "unknown",
                "duration": None,
                "error": str(e)
            }
    
    def _get_mime_type(self, filename: str) -> str:
        """Get MIME type from filename extension."""
        extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else "ogg"
        
        mime_types = {
            "ogg": "audio/ogg",
            "oga": "audio/ogg",
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "m4a": "audio/mp4",
            "aac": "audio/aac",
            "flac": "audio/flac",
            "wma": "audio/x-ms-wma",
            "opus": "audio/opus",
            "webm": "audio/webm",
        }
        
        return mime_types.get(extension, "audio/ogg")
