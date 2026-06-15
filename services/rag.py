"""
RAG (Retrieval Augmented Generation) system for knowledge base.
Uses embeddings and vector search for document retrieval.
"""
import sqlite3
from typing import List, Dict, Optional, Tuple
import google.generativeai as genai
from config import Config

genai.configure(api_key=Config.GEMINI_API_KEY)


class RAGService:
    """Service for RAG-based question answering from documents."""
    
    def __init__(self, db_path: str = None):
        """Initialize RAG service."""
        self.db_path = db_path or "knowledge_base.db"
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.init_db()
    
    def init_db(self):
        """Create knowledge base tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Documents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Document chunks table (for large documents)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER NOT NULL,
                    chunk_text TEXT NOT NULL,
                    chunk_index INTEGER,
                    embedding_text TEXT,
                    FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
                )
            """)
            
            # Create indices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_docs 
                ON documents(user_id, created_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_doc_chunks 
                ON document_chunks(document_id, chunk_index)
            """)
            
            conn.commit()
    
    def add_document(
        self,
        user_id: int,
        title: str,
        content: str,
        source: Optional[str] = None
    ) -> int:
        """
        Add document to knowledge base.
        
        Args:
            user_id: User ID who added the document
            title: Document title
            content: Document content
            source: Optional source (file name, URL, etc.)
            
        Returns:
            Document ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO documents (user_id, title, content, source)
                VALUES (?, ?, ?, ?)
            """, (user_id, title, content, source))
            doc_id = cursor.lastrowid
            
            # Chunk document for better retrieval
            chunks = self._chunk_text(content)
            
            for idx, chunk in enumerate(chunks):
                cursor.execute("""
                    INSERT INTO document_chunks (document_id, chunk_text, chunk_index, embedding_text)
                    VALUES (?, ?, ?, ?)
                """, (doc_id, chunk, idx, chunk[:1000]))  # Store first 1000 chars for search
            
            conn.commit()
            return doc_id
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to chunk
            chunk_size: Size of each chunk
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                last_newline = chunk.rfind('\n')
                break_point = max(last_period, last_newline)
                
                if break_point > chunk_size * 0.5:  # At least 50% of chunk
                    chunk = chunk[:break_point + 1]
                    end = start + break_point + 1
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def search_documents(
        self,
        query: str,
        user_id: Optional[int] = None,
        limit: int = 5
    ) -> List[Dict]:
        """
        Search documents using text matching.
        
        Args:
            query: Search query
            user_id: Optional user ID to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching document chunks
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Simple text search (can be enhanced with FTS)
            query_lower = query.lower()
            
            if user_id:
                cursor.execute("""
                    SELECT dc.chunk_text, d.title, d.source, dc.chunk_index
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    WHERE d.user_id = ? AND LOWER(dc.chunk_text) LIKE ?
                    ORDER BY dc.chunk_index
                    LIMIT ?
                """, (user_id, f'%{query_lower}%', limit))
            else:
                cursor.execute("""
                    SELECT dc.chunk_text, d.title, d.source, dc.chunk_index
                    FROM document_chunks dc
                    JOIN documents d ON dc.document_id = d.id
                    WHERE LOWER(dc.chunk_text) LIKE ?
                    ORDER BY dc.chunk_index
                    LIMIT ?
                """, (f'%{query_lower}%', limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'chunk': row[0],
                    'title': row[1],
                    'source': row[2],
                    'chunk_index': row[3]
                })
            
            return results
    
    async def ask_with_context(
        self,
        question: str,
        user_id: Optional[int] = None,
        max_context_chunks: int = 3
    ) -> str:
        """
        Answer question using RAG approach.
        
        Args:
            question: User's question
            user_id: Optional user ID for personalized search
            max_context_chunks: Maximum context chunks to include
            
        Returns:
            Answer with context
        """
        try:
            # Search relevant documents
            results = self.search_documents(question, user_id, max_context_chunks)
            
            if not results:
                return await self._answer_without_context(question)
            
            # Build context from retrieved chunks
            context = "\n\n".join([
                f"[{r['title']}]\n{r['chunk']}"
                for r in results
            ])
            
            # Generate answer with context
            prompt = f"""Quyidagi kontekst asosida savolga javob bering:

KONTEKST:
{context}

SAVOL: {question}

JAVOB:"""
            
            response = self.model.generate_content(prompt)
            
            # Add sources
            sources = list(set([r['title'] for r in results if r['title']]))
            sources_text = "\n\n📚 Manbalar: " + ", ".join(sources) if sources else ""
            
            return response.text.strip() + sources_text
            
        except Exception as e:
            return f"Xatolik: {str(e)}"
    
    async def _answer_without_context(self, question: str) -> str:
        """Answer question without RAG context."""
        prompt = f"""{question}

(Eslatma: Bu savol uchun knowledge base'da ma'lumot topilmadi. Umumiy bilim asosida javob berilmoqda.)"""
        
        response = self.model.generate_content(prompt)
        return response.text.strip()
    
    def get_user_documents(self, user_id: int, limit: int = 10) -> List[Dict]:
        """
        Get user's documents.
        
        Args:
            user_id: User ID
            limit: Maximum number of documents
            
        Returns:
            List of documents
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, source, created_at
                FROM documents
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (user_id, limit))
            
            docs = []
            for row in cursor.fetchall():
                docs.append({
                    'id': row[0],
                    'title': row[1],
                    'source': row[2],
                    'created_at': row[3]
                })
            
            return docs
    
    def delete_document(self, doc_id: int, user_id: int) -> bool:
        """
        Delete document from knowledge base.
        
        Args:
            doc_id: Document ID
            user_id: User ID (for verification)
            
        Returns:
            True if deleted, False otherwise
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM documents
                WHERE id = ? AND user_id = ?
            """, (doc_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_document_count(self, user_id: Optional[int] = None) -> int:
        """Get total document count."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if user_id:
                cursor.execute("""
                    SELECT COUNT(*) FROM documents WHERE user_id = ?
                """, (user_id,))
            else:
                cursor.execute("SELECT COUNT(*) FROM documents")
            
            return cursor.fetchone()[0]
