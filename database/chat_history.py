"""
SQLite database module for managing user chat history.
"""
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
from config import Config


class ChatHistoryDB:
    """Manages chat history storage using SQLite."""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection and create tables."""
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_db()
    
    def init_db(self):
        """Create necessary tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    message_type TEXT DEFAULT 'text'
                )
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_id 
                ON chat_history(user_id, timestamp)
            """)
            conn.commit()
    
    def add_message(
        self, 
        user_id: int, 
        role: str, 
        content: str, 
        message_type: str = 'text'
    ):
        """
        Add a message to chat history.
        
        Args:
            user_id: Telegram user ID
            role: 'user' or 'model'
            content: Message content
            message_type: Type of message (text, image, document, voice)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO chat_history (user_id, role, content, message_type)
                VALUES (?, ?, ?, ?)
            """, (user_id, role, content, message_type))
            conn.commit()
    
    def get_history(
        self, 
        user_id: int, 
        limit: int = None
    ) -> List[Dict[str, str]]:
        """
        Get chat history for a user in Gemini format.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of messages in format: [{"role": "user", "parts": ["text"]}]
        """
        limit = limit or Config.MAX_HISTORY_MESSAGES
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT role, content, message_type
                FROM chat_history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            
        # Reverse to get chronological order and format for Gemini
        history = []
        for role, content, msg_type in reversed(rows):
            history.append({
                "role": role,
                "parts": [content]
            })
        
        return history
    
    def clear_history(self, user_id: int):
        """Clear all chat history for a user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM chat_history WHERE user_id = ?
            """, (user_id,))
            conn.commit()
    
    def get_user_count(self) -> int:
        """Get total number of unique users."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) FROM chat_history
            """)
            return cursor.fetchone()[0]
    
    def get_message_count(self, user_id: Optional[int] = None) -> int:
        """Get total message count, optionally for specific user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            if user_id:
                cursor.execute("""
                    SELECT COUNT(*) FROM chat_history WHERE user_id = ?
                """, (user_id,))
            else:
                cursor.execute("""
                    SELECT COUNT(*) FROM chat_history
                """)
            return cursor.fetchone()[0]
