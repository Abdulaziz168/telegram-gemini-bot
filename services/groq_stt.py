"""
Groq STT (Speech-to-Text) service using Whisper-large-v3.
"""
from groq import Groq
from typing import Optional
import io
from config import Config


class GroqSTTService:
    """Service for converting speech to text using Groq Whisper API."""
    
    def __init__(self, model: str = "whisper-large-v3"):
        """
        Initialize Groq STT service.
        
        Args:
            model: Whisper model to use (default: whisper-large-v3)
        """
        self.client = Groq(api_key=Config.GROQ_API_KEY)
        self.model = model
    
    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        filename: str = "audio.ogg"
    ) -> str:
        """
        Transcribe audio to text.
        
        Args:
            audio_data: Audio file bytes
            language: Optional language code (e.g., 'uz', 'ru', 'en')
            filename: Filename with extension (needed for format detection)
            
        Returns:
            Transcribed text
        """
        try:
            # Create file-like object
            audio_file = io.BytesIO(audio_data)
            audio_file.name = filename
            
            # Prepare transcription parameters
            params = {
                "file": audio_file,
                "model": self.model,
                "response_format": "text",
            }
            
            # Add language if specified
            if language:
                params["language"] = language
            
            # Transcribe
            transcription = self.client.audio.transcriptions.create(**params)
            
            return transcription.strip()
            
        except Exception as e:
            error_msg = f"Groq STT xatosi: {str(e)}"
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
            audio_file = io.BytesIO(audio_data)
            audio_file.name = filename
            
            params = {
                "file": audio_file,
                "model": self.model,
                "response_format": "verbose_json",
            }
            
            if language:
                params["language"] = language
            
            response = self.client.audio.transcriptions.create(**params)
            
            return {
                "text": response.text.strip(),
                "language": getattr(response, 'language', language or 'unknown'),
                "duration": getattr(response, 'duration', None),
            }
            
        except Exception as e:
            error_msg = f"Groq STT metadata xatosi: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "text": f"Xatolik yuz berdi: {str(e)}",
                "language": "unknown",
                "duration": None,
                "error": str(e)
            }
    
    def detect_language(self, audio_data: bytes, filename: str = "audio.ogg") -> str:
        """
        Detect language from audio (synchronous version for quick detection).
        
        Args:
            audio_data: Audio file bytes
            filename: Filename with extension
            
        Returns:
            Detected language code
        """
        try:
            audio_file = io.BytesIO(audio_data)
            audio_file.name = filename
            
            response = self.client.audio.transcriptions.create(
                file=audio_file,
                model=self.model,
                response_format="verbose_json"
            )
            
            return getattr(response, 'language', 'unknown')
            
        except Exception as e:
            print(f"❌ Til aniqlashda xatolik: {str(e)}")
            return 'unknown'
