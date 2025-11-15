"""File processing utilities."""

import io
import uuid
from typing import Dict, List, Optional

import PyPDF2
from docx import Document

from app.core.exceptions import FileProcessingError
from app.core.logging import get_logger

logger = get_logger(__name__)


class FileProcessor:
    """File processing utility class."""
    
    def __init__(self):
        self.supported_types = ["pdf", "docx", "doc"]
    
    def extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            logger.info("PDF text extraction successful", pages=len(pdf_reader.pages))
            return text.strip()
            
        except Exception as e:
            logger.error("PDF text extraction failed", error=str(e))
            raise FileProcessingError(
                f"Failed to extract text from PDF: {str(e)}",
                file_type="pdf"
            )
    
    def extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file."""
        try:
            doc_file = io.BytesIO(file_content)
            doc = Document(doc_file)
            
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            logger.info("DOCX text extraction successful", paragraphs=len(doc.paragraphs))
            return text.strip()
            
        except Exception as e:
            logger.error("DOCX text extraction failed", error=str(e))
            raise FileProcessingError(
                f"Failed to extract text from DOCX: {str(e)}",
                file_type="docx"
            )
    
    def extract_text_from_doc(self, file_content: bytes) -> str:
        """Extract text from DOC file."""
        # For now, we'll treat DOC files as unsupported
        # In a real implementation, you'd use python-docx2txt or similar
        raise FileProcessingError(
            "DOC file format not supported. Please convert to DOCX or PDF.",
            file_type="doc"
        )
    
    def extract_text(self, file_content: bytes, file_type: str) -> str:
        """Extract text from file based on type."""
        if file_type.lower() not in self.supported_types:
            raise FileProcessingError(
                f"Unsupported file type: {file_type}",
                file_type=file_type
            )
        
        if file_type.lower() == "pdf":
            return self.extract_text_from_pdf(file_content)
        elif file_type.lower() == "docx":
            return self.extract_text_from_docx(file_content)
        elif file_type.lower() == "doc":
            return self.extract_text_from_doc(file_content)
        else:
            raise FileProcessingError(
                f"Unknown file type: {file_type}",
                file_type=file_type
            )
    
    def validate_file_size(self, file_content: bytes, max_size: int) -> bool:
        """Validate file size."""
        if len(file_content) > max_size:
            raise FileProcessingError(
                f"File too large. Max size: {max_size} bytes",
                file_type="unknown"
            )
        return True
    
    def generate_file_id(self) -> str:
        """Generate unique file ID."""
        return str(uuid.uuid4())
    
    def get_file_info(self, file_content: bytes, file_name: str) -> Dict[str, any]:
        """Get file information."""
        return {
            "file_id": self.generate_file_id(),
            "file_name": file_name,
            "file_size": len(file_content),
            "file_type": file_name.split(".")[-1].lower() if "." in file_name else "unknown"
        }