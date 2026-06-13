"""
User preferences and settings management.
"""
import sqlite3
import json
from typing import Optional, Dict, Any
from config import Config


class UserPreferencesDB:
    """Manages user preferences and settings."""
    
    def __init__(self, db_path: str = None):
        """Initialize user preferences database."""
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_db()
    
    def init_db(self):
        """Create user preferences table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # User preferences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    language TEXT DEFAULT 'uz',
                    ai_personality TEXT DEFAULT 'friendly',
                    response_length TEXT DEFAULT 'medium',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User stats table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_stats (
                    user_id INTEGER PRIMARY KEY,
                    total_messages INTEGER DEFAULT 0,
                    total_images INTEGER DEFAULT 0,
                    total_documents INTEGER DEFAULT 0,
                    total_voice INTEGER DEFAULT 0,
                    first_interaction DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_interaction DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Bookmarks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    message_text TEXT NOT NULL,
                    tags TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_preferences(user_id)
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_bookmarks_user 
                ON bookmarks(user_id, created_at DESC)
            """)
            
            conn.commit()
    
    def get_preferences(self, user_id: int) -> Dict[str, str]:
        """
        Get user preferences.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User preferences dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT language, ai_personality, response_length
                FROM user_preferences
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "language": row[0],
                    "ai_personality": row[1],
                    "response_length": row[2]
                }
            else:
                # Create default preferences
                self.set_preference(user_id, "language", "uz")
                return {
                    "language": "uz",
                    "ai_personality": "friendly",
                    "response_length": "medium"
                }
    
    def set_preference(self, user_id: int, key: str, value: str):
        """
        Set user preference.
        
        Args:
            user_id: Telegram user ID
            key: Preference key (language, ai_personality, response_length)
            value: Preference value
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if user exists
            cursor.execute("""
                SELECT user_id FROM user_preferences WHERE user_id = ?
            """, (user_id,))
            
            if cursor.fetchone():
                # Update existing
                cursor.execute(f"""
                    UPDATE user_preferences
                    SET {key} = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (value, user_id))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO user_preferences (user_id, language, ai_personality, response_length)
                    VALUES (?, ?, ?, ?)
                """, (user_id, "uz", "friendly", "medium"))
                
                cursor.execute(f"""
                    UPDATE user_preferences
                    SET {key} = ?
                    WHERE user_id = ?
                """, (value, user_id))
            
            conn.commit()
    
    def update_stats(self, user_id: int, message_type: str = "text"):
        """
        Update user statistics.
        
        Args:
            user_id: Telegram user ID
            message_type: Type of message (text, image, document, voice)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if stats exist
            cursor.execute("""
                SELECT user_id FROM user_stats WHERE user_id = ?
            """, (user_id,))
            
            if cursor.fetchone():
                # Update existing
                if message_type == "text":
                    column = "total_messages"
                elif message_type == "image":
                    column = "total_images"
                elif message_type == "document":
                    column = "total_documents"
                elif message_type == "voice":
                    column = "total_voice"
                else:
                    column = "total_messages"
                
                cursor.execute(f"""
                    UPDATE user_stats
                    SET {column} = {column} + 1,
                        last_interaction = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """, (user_id,))
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO user_stats (user_id, total_messages)
                    VALUES (?, 1)
                """, (user_id,))
            
            conn.commit()
    
    def get_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User statistics dictionary
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT total_messages, total_images, total_documents, 
                       total_voice, first_interaction, last_interaction
                FROM user_stats
                WHERE user_id = ?
            """, (user_id,))
            
            row = cursor.fetchone()
            
            if row:
                return {
                    "total_messages": row[0],
                    "total_images": row[1],
                    "total_documents": row[2],
                    "total_voice": row[3],
                    "first_interaction": row[4],
                    "last_interaction": row[5]
                }
            else:
                return {
                    "total_messages": 0,
                    "total_images": 0,
                    "total_documents": 0,
                    "total_voice": 0,
                    "first_interaction": None,
                    "last_interaction": None
                }
    
    def add_bookmark(self, user_id: int, message_text: str, tags: Optional[str] = None):
        """
        Add a bookmark.
        
        Args:
            user_id: Telegram user ID
            message_text: Message text to bookmark
            tags: Optional comma-separated tags
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bookmarks (user_id, message_text, tags)
                VALUES (?, ?, ?)
            """, (user_id, message_text, tags))
            conn.commit()
    
    def get_bookmarks(self, user_id: int, limit: int = 10) -> list:
        """
        Get user bookmarks.
        
        Args:
            user_id: Telegram user ID
            limit: Maximum number of bookmarks
            
        Returns:
            List of bookmarks
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, message_text, tags, created_at
                FROM bookmarks
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            
            bookmarks = []
            for row in rows:
                bookmarks.append({
                    "id": row[0],
                    "message": row[1],
                    "tags": row[2],
                    "created_at": row[3]
                })
            
            return bookmarks
    
    def delete_bookmark(self, user_id: int, bookmark_id: int):
        """
        Delete a bookmark.
        
        Args:
            user_id: Telegram user ID
            bookmark_id: Bookmark ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM bookmarks
                WHERE id = ? AND user_id = ?
            """, (bookmark_id, user_id))
            conn.commit()
    
    def get_all_user_ids(self) -> list:
        """Get all user IDs for broadcasting."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT user_id FROM user_preferences
            """)
            return [row[0] for row in cursor.fetchall()]
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total users
            cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_preferences")
            total_users = cursor.fetchone()[0]
            
            # Total messages
            cursor.execute("SELECT SUM(total_messages) FROM user_stats")
            total_messages = cursor.fetchone()[0] or 0
            
            # Total images
            cursor.execute("SELECT SUM(total_images) FROM user_stats")
            total_images = cursor.fetchone()[0] or 0
            
            # Total documents
            cursor.execute("SELECT SUM(total_documents) FROM user_stats")
            total_documents = cursor.fetchone()[0] or 0
            
            # Total voice
            cursor.execute("SELECT SUM(total_voice) FROM user_stats")
            total_voice = cursor.fetchone()[0] or 0
            
            return {
                "total_users": total_users,
                "total_messages": total_messages,
                "total_images": total_images,
                "total_documents": total_documents,
                "total_voice": total_voice
            }
