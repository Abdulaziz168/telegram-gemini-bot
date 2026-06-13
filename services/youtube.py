"""
YouTube video analysis service.
"""
import re
from typing import Optional, Dict
import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)


class YouTubeService:
    """Service for analyzing YouTube videos."""
    
    def __init__(self):
        """Initialize YouTube service."""
        self.model = genai.GenerativeModel("gemini-1.5-flash")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID or None
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def analyze_video_description(
        self,
        video_url: str,
        question: Optional[str] = None
    ) -> str:
        """
        Analyze YouTube video (requires video description/transcript).
        
        Args:
            video_url: YouTube video URL
            question: Specific question about the video
            
        Returns:
            Analysis result
        """
        try:
            video_id = self.extract_video_id(video_url)
            
            if not video_id:
                return "❌ Noto'g'ri YouTube URL"
            
            if question:
                prompt = f"""YouTube video haqida savol: {question}

Video URL: {video_url}

Iltimos, bu video haqida ma'lumot bering."""
            else:
                prompt = f"""YouTube video haqida ma'lumot bering:

Video URL: {video_url}

Video mavzusi, mazmuni va asosiy fikrlarni tushuntiring."""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Video tahlili xatosi: {str(e)}"
    
    async def suggest_content(self, topic: str) -> str:
        """
        Suggest YouTube content ideas.
        
        Args:
            topic: Content topic
            
        Returns:
            Content suggestions
        """
        try:
            prompt = f""""{topic}" mavzusida YouTube video yaratish uchun 5 ta g'oya taklif qiling.

Har bir g'oya uchun:
- Video sarlavhasi
- Qisqacha tavsif
- Maqsadli auditoriya

G'oyalar:"""
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Xatolik: {str(e)}"
