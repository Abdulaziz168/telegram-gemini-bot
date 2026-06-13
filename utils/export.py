"""
Export and import functionality for chat history.
"""
import json
import io
from datetime import datetime
from typing import List, Dict, Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class ExportService:
    """Service for exporting and importing chat history."""
    
    def __init__(self):
        """Initialize export service."""
        pass
    
    def export_to_json(self, history: List[Dict], user_id: int) -> io.BytesIO:
        """
        Export chat history to JSON.
        
        Args:
            history: Chat history list
            user_id: User ID
            
        Returns:
            BytesIO object with JSON data
        """
        export_data = {
            "user_id": user_id,
            "exported_at": datetime.now().isoformat(),
            "total_messages": len(history),
            "history": history
        }
        
        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
        return io.BytesIO(json_str.encode('utf-8'))
    
    def export_to_txt(self, history: List[Dict], user_id: int) -> io.BytesIO:
        """
        Export chat history to plain text.
        
        Args:
            history: Chat history list
            user_id: User ID
            
        Returns:
            BytesIO object with text data
        """
        lines = [
            f"Suhbat tarixi - Foydalanuvchi ID: {user_id}",
            f"Export sanasi: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Jami xabarlar: {len(history)}",
            "=" * 60,
            ""
        ]
        
        for idx, msg in enumerate(history, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('parts', [''])[0] if msg.get('parts') else msg.get('content', '')
            
            role_name = "👤 Siz" if role == "user" else "🤖 AI"
            
            lines.append(f"{idx}. {role_name}:")
            lines.append(content)
            lines.append("-" * 60)
            lines.append("")
        
        txt_content = "\n".join(lines)
        return io.BytesIO(txt_content.encode('utf-8'))
    
    def export_to_pdf(self, history: List[Dict], user_id: int) -> io.BytesIO:
        """
        Export chat history to PDF.
        
        Args:
            history: Chat history list
            user_id: User ID
            
        Returns:
            BytesIO object with PDF data
        """
        buffer = io.BytesIO()
        
        # Create PDF
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Define styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor='#2c3e50',
            spaceAfter=30,
            alignment=TA_LEFT
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor='#34495e',
            spaceAfter=12
        )
        
        user_style = ParagraphStyle(
            'UserMessage',
            parent=styles['Normal'],
            fontSize=11,
            textColor='#2c3e50',
            leftIndent=20,
            spaceAfter=10
        )
        
        ai_style = ParagraphStyle(
            'AIMessage',
            parent=styles['Normal'],
            fontSize=11,
            textColor='#16a085',
            leftIndent=20,
            spaceAfter=10
        )
        
        # Add title
        title = Paragraph(f"<b>Suhbat Tarixi</b>", title_style)
        elements.append(title)
        elements.append(Spacer(1, 12))
        
        # Add metadata
        metadata = f"""
        <b>Foydalanuvchi ID:</b> {user_id}<br/>
        <b>Export sanasi:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>
        <b>Jami xabarlar:</b> {len(history)}
        """
        elements.append(Paragraph(metadata, styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Add messages
        for idx, msg in enumerate(history, 1):
            role = msg.get('role', 'unknown')
            content = msg.get('parts', [''])[0] if msg.get('parts') else msg.get('content', '')
            
            # Clean content for PDF
            content = content.replace('<', '&lt;').replace('>', '&gt;')
            
            if role == "user":
                heading = Paragraph(f"<b>#{idx}. Foydalanuvchi:</b>", heading_style)
                message = Paragraph(content, user_style)
            else:
                heading = Paragraph(f"<b>#{idx}. AI Javob:</b>", heading_style)
                message = Paragraph(content, ai_style)
            
            elements.append(heading)
            elements.append(message)
            elements.append(Spacer(1, 15))
            
            # Add page break every 10 messages
            if idx % 10 == 0 and idx < len(history):
                elements.append(PageBreak())
        
        # Build PDF
        doc.build(elements)
        
        buffer.seek(0)
        return buffer
    
    def import_from_json(self, json_data: str) -> Optional[Dict]:
        """
        Import chat history from JSON.
        
        Args:
            json_data: JSON string
            
        Returns:
            Parsed data or None
        """
        try:
            data = json.loads(json_data)
            
            if 'history' not in data:
                return None
            
            return {
                'user_id': data.get('user_id'),
                'history': data['history'],
                'exported_at': data.get('exported_at')
            }
        except Exception as e:
            print(f"Import error: {e}")
            return None
