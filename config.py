"""
Configuration module for loading environment variables securely.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class Config:
    """Configuration class for bot settings."""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Groq API (for STT)
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'chat_history.db')
    
    # Bot Settings
    MAX_HISTORY_MESSAGES = int(os.getenv('MAX_HISTORY_MESSAGES', '10'))
    
    @classmethod
    def validate(cls):
        """Validate that all required environment variables are set."""
        required_vars = {
            'TELEGRAM_BOT_TOKEN': cls.TELEGRAM_BOT_TOKEN,
            'GEMINI_API_KEY': cls.GEMINI_API_KEY,
            'GROQ_API_KEY': cls.GROQ_API_KEY,
        }
        
        missing = [var for var, value in required_vars.items() if not value]
        
        if missing:
            raise ValueError(
                f"Quyidagi muhim environment variables topilmadi: {', '.join(missing)}\n"
                f".env faylini yarating va kerakli tokenlarni kiriting."
            )
        
        return True


# Validate configuration on import
if __name__ != '__main__':
    try:
        Config.validate()
    except ValueError as e:
        print(f"⚠️  Konfiguratsiya xatosi: {e}")
