"""
Keyboard and button builders for bot UI.
"""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class KeyboardBuilder:
    """Builder for various keyboard types."""
    
    @staticmethod
    def main_menu() -> ReplyKeyboardMarkup:
        """Create main menu keyboard."""
        builder = ReplyKeyboardBuilder()
        
        # Row 1
        builder.button(text="💬 Suhbat")
        builder.button(text="🖼 Rasm tahlili")
        
        # Row 2
        builder.button(text="📄 Hujjat")
        builder.button(text="🎤 Ovoz")
        
        # Row 3
        builder.button(text="⚙️ Sozlamalar")
        builder.button(text="📊 Statistika")
        
        # Row 4
        builder.button(text="❓ Yordam")
        
        builder.adjust(2, 2, 2, 1)
        return builder.as_markup(resize_keyboard=True)
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Create settings inline keyboard."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="🌐 Til / Language", callback_data="settings_language")
        builder.button(text="🤖 AI Shaxsiyati", callback_data="settings_personality")
        builder.button(text="📏 Javob uzunligi", callback_data="settings_length")
        builder.button(text="🗑 Tarixni tozalash", callback_data="settings_clear")
        builder.button(text="📥 Export", callback_data="settings_export")
        builder.button(text="⭐ Favorites", callback_data="settings_favorites")
        builder.button(text="🔙 Orqaga", callback_data="main_menu")
        
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def language_menu() -> InlineKeyboardMarkup:
        """Create language selection keyboard."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="🇺🇿 O'zbek", callback_data="lang_uz")
        builder.button(text="🇷🇺 Русский", callback_data="lang_ru")
        builder.button(text="🇬🇧 English", callback_data="lang_en")
        builder.button(text="🔙 Orqaga", callback_data="back_settings")
        
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def personality_menu() -> InlineKeyboardMarkup:
        """Create AI personality selection keyboard."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="🎩 Rasmiy", callback_data="personality_formal")
        builder.button(text="😊 Do'stona", callback_data="personality_friendly")
        builder.button(text="🤓 Professional", callback_data="personality_professional")
        builder.button(text="😄 Kulgili", callback_data="personality_funny")
        builder.button(text="🔙 Orqaga", callback_data="back_settings")
        
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def response_length_menu() -> InlineKeyboardMarkup:
        """Create response length selection keyboard."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="📝 Qisqa", callback_data="length_short")
        builder.button(text="📄 O'rtacha", callback_data="length_medium")
        builder.button(text="📚 Batafsil", callback_data="length_long")
        builder.button(text="🔙 Orqaga", callback_data="back_settings")
        
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def export_menu() -> InlineKeyboardMarkup:
        """Create export format selection keyboard."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="📄 PDF", callback_data="export_pdf")
        builder.button(text="📋 JSON", callback_data="export_json")
        builder.button(text="📝 TXT", callback_data="export_txt")
        builder.button(text="🔙 Orqaga", callback_data="back_settings")
        
        builder.adjust(1)
        return builder.as_markup()
    
    @staticmethod
    def confirm_action(action: str) -> InlineKeyboardMarkup:
        """Create confirmation keyboard."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="✅ Ha", callback_data=f"confirm_{action}")
        builder.button(text="❌ Yo'q", callback_data=f"cancel_{action}")
        
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def admin_menu() -> InlineKeyboardMarkup:
        """Create admin panel keyboard."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="👥 Foydalanuvchilar", callback_data="admin_users")
        builder.button(text="📢 Broadcast", callback_data="admin_broadcast")
        builder.button(text="📊 Statistika", callback_data="admin_stats")
        builder.button(text="🗂 Loglar", callback_data="admin_logs")
        builder.button(text="⚙️ Sozlamalar", callback_data="admin_settings")
        
        builder.adjust(2, 2, 1)
        return builder.as_markup()
    
    @staticmethod
    def translation_menu() -> InlineKeyboardMarkup:
        """Create translation target language keyboard."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="🇺🇿 O'zbek", callback_data="translate_uz")
        builder.button(text="🇷🇺 Rus", callback_data="translate_ru")
        builder.button(text="🇬🇧 Ingliz", callback_data="translate_en")
        builder.button(text="🇹🇷 Turk", callback_data="translate_tr")
        builder.button(text="🇩🇪 Nemis", callback_data="translate_de")
        builder.button(text="🇫🇷 Fransuz", callback_data="translate_fr")
        
        builder.adjust(2)
        return builder.as_markup()
    
    @staticmethod
    def summarize_menu() -> InlineKeyboardMarkup:
        """Create summarization options keyboard."""
        builder = InlineKeyboardBuilder()
        
        builder.button(text="📝 Qisqa", callback_data="summary_short")
        builder.button(text="📄 O'rtacha", callback_data="summary_medium")
        builder.button(text="📚 Batafsil", callback_data="summary_long")
        builder.button(text="🎯 Asosiy fikrlar", callback_data="summary_keypoints")
        builder.button(text="⚡ TL;DR", callback_data="summary_tldr")
        
        builder.adjust(2, 2, 1)
        return builder.as_markup()
