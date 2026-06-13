"""
Gemini AI service for multimodal interactions (text, images, documents).
"""
import google.generativeai as genai
from typing import List, Dict, Optional, Union
import PIL.Image
import io
from config import Config

# Configure Gemini API
genai.configure(api_key=Config.GEMINI_API_KEY)


class GeminiService:
    """Service for interacting with Google Gemini AI."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Gemini service.
        
        Args:
            model_name: Name of the Gemini model to use
        """
        self.model = genai.GenerativeModel(model_name)
        
        # Safety settings - moderate blocking
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
        ]
        
        # Generation config
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
    
    async def generate_response(
        self,
        prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        image_data: Optional[bytes] = None,
        document_data: Optional[bytes] = None
    ) -> str:
        """
        Generate response from Gemini with optional multimodal input.
        
        Args:
            prompt: User's text prompt
            history: Chat history in Gemini format
            image_data: Optional image bytes
            document_data: Optional document bytes (PDF, etc.)
            
        Returns:
            Generated text response
        """
        try:
            # Start chat with history
            chat = self.model.start_chat(history=history or [])
            
            # Prepare message parts
            message_parts = []
            
            # Add image if provided
            if image_data:
                image = PIL.Image.open(io.BytesIO(image_data))
                message_parts.append(image)
            
            # Add document if provided (for PDFs)
            if document_data:
                # For PDF files, we can upload them
                # Gemini supports PDF analysis
                message_parts.append({
                    "mime_type": "application/pdf",
                    "data": document_data
                })
            
            # Add text prompt
            message_parts.append(prompt)
            
            # Generate response
            response = chat.send_message(
                message_parts,
                safety_settings=self.safety_settings,
                generation_config=self.generation_config
            )
            
            return response.text
            
        except Exception as e:
            error_msg = f"Gemini xatosi: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Kechirasiz, javob berishda xatolik yuz berdi: {str(e)}"
    
    async def analyze_image(
        self,
        image_data: bytes,
        prompt: str = "Bu rasmda nima ko'rsatilgan? Batafsil tahlil qiling."
    ) -> str:
        """
        Analyze an image with Gemini Vision.
        
        Args:
            image_data: Image bytes
            prompt: Analysis prompt
            
        Returns:
            Analysis result
        """
        try:
            image = PIL.Image.open(io.BytesIO(image_data))
            
            response = self.model.generate_content(
                [prompt, image],
                safety_settings=self.safety_settings,
                generation_config=self.generation_config
            )
            
            return response.text
            
        except Exception as e:
            error_msg = f"Rasm tahlili xatosi: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Rasmni tahlil qilishda xatolik: {str(e)}"
    
    async def analyze_document(
        self,
        document_data: bytes,
        prompt: str = "Bu hujjatni tahlil qiling va mazmunini tushuntiring.",
        mime_type: str = "application/pdf"
    ) -> str:
        """
        Analyze a document (PDF, etc.) with Gemini.
        
        Args:
            document_data: Document bytes
            prompt: Analysis prompt
            mime_type: MIME type of document
            
        Returns:
            Analysis result
        """
        try:
            # Upload file to Gemini
            uploaded_file = genai.upload_file(
                io.BytesIO(document_data),
                mime_type=mime_type
            )
            
            response = self.model.generate_content(
                [prompt, uploaded_file],
                safety_settings=self.safety_settings,
                generation_config=self.generation_config
            )
            
            return response.text
            
        except Exception as e:
            error_msg = f"Hujjat tahlili xatosi: {str(e)}"
            print(f"❌ {error_msg}")
            return f"Hujjatni tahlil qilishda xatolik: {str(e)}"
    
    def escape_markdown(self, text: str) -> str:
        """
        Escape markdown special characters for Telegram.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text safe for Telegram MarkdownV2
        """
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
