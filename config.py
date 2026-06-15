"""
Configuration module for loading environment variables securely.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def get_base_path():
    """Get the base path for bundled files (works for both dev and PyInstaller exe)."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller exe
        return Path(sys._MEIPASS)
    else:
        # Running as script
        return Path(__file__).parent


def get_runtime_path():
    """Get the runtime path (where the exe is located)."""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).parent


# Try to load .env from exe directory first, then from bundled path
runtime_env = get_runtime_path() / '.env'
bundled_env = get_base_path() / '.env'

if runtime_env.exists():
    load_dotenv(dotenv_path=runtime_env)
elif bundled_env.exists():
    load_dotenv(dotenv_path=bundled_env)

class Config:
    """Configuration class for bot settings."""
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Groq API (for STT)
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Database - always store next to exe (not inside temp folder)
    DATABASE_PATH = os.getenv('DATABASE_PATH', str(get_runtime_path() / 'chat_history.db'))
    
    # Bot Settings
    MAX_HISTORY_MESSAGES = int(os.getenv('MAX_HISTORY_MESSAGES', '10'))
    
    # Admin Settings
    ADMIN_IDS = os.getenv('ADMIN_IDS', '')
    OWNER_ID = int(os.getenv('OWNER_ID', '0')) if os.getenv('OWNER_ID') else 0
    
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
