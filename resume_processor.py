import os
import json
from pathlib import Path
from datetime import datetime
import PyPDF2
import pytesseract
from PIL import Image
import mimetypes
from config import DATASETS_DIR

class ResumeProcessor:
    """Process resume files and extract text"""
    
    def __init__(self):
        self.resumes_dir = DATASETS_DIR / "resumes"
        self.resumes_dir.mkdir(exist_ok=True)
        print("✅ Resume Processor initialized")
    
    def process_resume(self, file, candidate_name=None):
        """
        Process resume file and extract text
        
        Args:
            file: File object from Flask request
            candidate_name: Optional candidate name
        
        Returns:
            Dict with success, resume_text, and metadata
        """
        try:
            # Get filename
            filename = file.filename if hasattr(file, 'filename') else 'resume'
            file_ext = Path(filename).suffix.lower()
            
            print(f"\n📄 PROCESSING RESUME")
            print(f"   Filename: {filename}")
            print(f"   Format: {file_ext}")
            
            # Extract text based on file type
            if file_ext == '.pdf':
                text = self._extract_from_pdf(file)
            elif file_ext in ['.png', '.jpg', '.jpeg']:
                text = self._extract_from_image(file)
            elif file_ext == '.txt':
                text = self._extract_from_txt(file)
            else:
                raise ValueError(f"Unsupported format: {file_ext}")
            
            # Create metadata
            if not candidate_name:
                candidate_name = Path(filename).stem
            
            metadata = {
                'candidate_name': candidate_name,
                'original_filename': filename,
                'file_format': file_ext.strip('.'),
                'processing_date': datetime.now().isoformat(),
                'text_length': len(text),
                'words': len(text.split())
            }
            
            print(f"   ✅ Extracted {metadata['words']} words")
            
            return {
                'success': True,
                'resume_text': text,
                'metadata': metadata
            }
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {
                'success': False,
                'error': str(e),
                'resume_text': ''
            }
    
    def _extract_from_pdf(self, file):
        """Extract text from PDF"""
        text = ""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"PDF extraction failed: {e}")
    
    def _extract_from_image(self, file):
        """Extract text from image using OCR"""
        try:
            img = Image.open(file)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            text = pytesseract.image_to_string(img)
            return text.strip()
        except Exception as e:
            raise Exception(f"Image OCR extraction failed: {e}")
    
    def _extract_from_txt(self, file):
        """Extract text from text file"""
        try:
            content = file.read()
            if isinstance(content, bytes):
                return content.decode('utf-8').strip()
            return content.strip()
        except Exception as e:
            raise Exception(f"Text extraction failed: {e}")