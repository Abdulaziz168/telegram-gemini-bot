"""
Translation service using Google Gemini for context-aware translation.
"""
from typing import Optional
import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)


class TranslationService:
    """Service for translating text between languages."""
    
    def __init__(self):
        """Initialize translation service."""
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    async def translate(
        self, 
        text: str, 
        target_lang: str = "uz",
        source_lang: Optional[str] = None
    ) -> str:
        """
        Translate text to target language.
        
        Args:
            text: Text to translate
            target_lang: Target language code (uz, ru, en, etc.)
            source_lang: Source language (auto-detect if None)
            
        Returns:
            Translated text
        """
        try:
            lang_names = {
                "uz": "O'zbek",
                "ru": "Rus",
                "en": "Ingliz",
                "tr": "Turk",
                "ar": "Arab",
                "de": "Nemis",
                "fr": "Fransuz",
                "es": "Ispaniya",
                "zh": "Xitoy",
                "ja": "Yapon",
                "ko": "Koreys"
            }
            
            target_name = lang_names.get(target_lang, target_lang.upper())
            
            if source_lang:
                source_name = lang_names.get(source_lang, source_lang.upper())
                prompt = f"Quyidagi matnni {source_name} tilidan {target_name} tiliga tarjima qiling. Faqat tarjimani qaytaring, boshqa hech narsa yozMANG:\n\n{text}"
            else:
                prompt = f"Quyidagi matnni {target_name} tiliga tarjima qiling. Faqat tarjimani qaytaring, boshqa hech narsa yozMANG:\n\n{text}"
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Tarjima xatosi: {str(e)}"
    
    async def detect_language(self, text: str) -> str:
        """
        Detect language of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code
        """
        try:
            prompt = f"Quyidagi matn qaysi tilda yozilgan? Faqat til kodini qaytaring (uz, ru, en, etc.):\n\n{text}"
            
            response = self.model.generate_content(prompt)
            return response.text.strip().lower()
            
        except Exception as e:
            return "unknown"
    
    async def translate_with_context(
        self,
        text: str,
        target_lang: str,
        context: Optional[str] = None
    ) -> str:
        """
        Translate with contextual understanding.
        
        Args:
            text: Text to translate
            target_lang: Target language
            context: Additional context for better translation
            
        Returns:
            Contextual translation
        """
        try:
            lang_names = {
                "uz": "O'zbek",
                "ru": "Rus",
                "en": "Ingliz"
            }
            
            target_name = lang_names.get(target_lang, target_lang)
            
            if context:
                prompt = f"""Kontekst: {context}

Quyidagi matnni {target_name} tiliga kontekstni hisobga olib tarjima qiling:

{text}

Faqat tarjimani qaytaring."""
            else:
                prompt = f"Quyidagi matnni {target_name} tiliga tarjima qiling. Faqat tarjimani qaytaring:\n\n{text}"
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Tarjima xatosi: {str(e)}"
