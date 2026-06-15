"""
User states for multi-step conversations.
"""
from aiogram.fsm.state import State, StatesGroup


class UserStates(StatesGroup):
    """User conversation states."""
    
    # Main states
    idle = State()
    chatting = State()
    
    # Translation states
    waiting_for_translation_text = State()
    waiting_for_translation_target = State()
    
    # Summarization states
    waiting_for_summary_text = State()
    waiting_for_summary_options = State()
    
    # Export states
    choosing_export_format = State()
    
    # Admin states
    admin_broadcast = State()
    admin_waiting_broadcast_message = State()
    
    # Bookmark states
    waiting_for_bookmark_tag = State()


class ConversationData:
    """Temporary conversation data storage."""
    
    def __init__(self):
        """Initialize conversation data."""
        self.user_data = {}
    
    def set(self, user_id: int, key: str, value):
        """Set user data."""
        if user_id not in self.user_data:
            self.user_data[user_id] = {}
        self.user_data[user_id][key] = value
    
    def get(self, user_id: int, key: str, default=None):
        """Get user data."""
        return self.user_data.get(user_id, {}).get(key, default)
    
    def clear(self, user_id: int, key: str = None):
        """Clear user data."""
        if key:
            if user_id in self.user_data:
                self.user_data[user_id].pop(key, None)
        else:
            self.user_data.pop(user_id, None)


# Global conversation data instance
conversation_data = ConversationData()
