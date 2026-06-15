"""
Text summarization service using Gemini AI.
"""
import google.generativeai as genai
from typing import Optional
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)


class SummarizerService:
    """Service for summarizing text content."""
    
    def __init__(self):
        """Initialize summarizer service."""
        self.model = genai.GenerativeModel("gemini-2.5-flash")
    
    async def summarize(
        self,
        text: str,
        max_length: Optional[str] = "medium",
        language: str = "uz"
    ) -> str:
        """
        Summarize text content.
        
        Args:
            text: Text to summarize
            max_length: Summary length (short/medium/long)
            language: Output language
            
        Returns:
            Summarized text
        """
        try:
            length_instructions = {
                "short": "2-3 jumlada qisqacha",
                "medium": "5-7 jumlada o'rtacha",
                "long": "batafsil"
            }
            
            length_instr = length_instructions.get(max_length, "o'rtacha")
            
            lang_names = {
                "uz": "O'zbek",
                "ru": "Rus",
                "en": "Ingliz"
            }
            lang_name = lang_names.get(language, "O'zbek")
            
            prompt = f"""Quyidagi matnni {lang_name} tilida {length_instr} xulosalang:

{text}

Xulosa:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Xulosalashda xatolik: {str(e)}"
    
    async def summarize_key_points(self, text: str, language: str = "uz") -> str:
        """
        Extract key points from text.
        
        Args:
            text: Text to analyze
            language: Output language
            
        Returns:
            Key points as bullet list
        """
        try:
            lang_names = {"uz": "O'zbek", "ru": "Rus", "en": "Ingliz"}
            lang_name = lang_names.get(language, "O'zbek")
            
            prompt = f"""Quyidagi matndagi asosiy fikrlarni {lang_name} tilida bullet points shaklida ajratib chiqaring:

{text}

Asosiy fikrlar:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Tahlil xatosi: {str(e)}"
    
    async def tldr(self, text: str) -> str:
        """
        Generate TL;DR (Too Long; Didn't Read) summary.
        
        Args:
            text: Text to summarize
            
        Returns:
            Very brief summary
        """
        try:
            prompt = f"""Quyidagi matnni 1-2 jumlada juda qisqa xulosalang (TL;DR):

{text}

TL;DR:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Xatolik: {str(e)}"
