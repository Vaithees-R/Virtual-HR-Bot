"""
Resume Processor Module
Handles extraction of text from PDF, PNG, JPG, and TXT files
"""

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
    """Process resume files and extract text content"""
    
    SUPPORTED_FORMATS = {
        'application/pdf': 'pdf',
        'image/png': 'png',
        'image/jpeg': 'jpg',
        'text/plain': 'txt'
    }
    
    def __init__(self):
        self.resumes_dir = DATASETS_DIR / "resumes"
        self.resumes_dir.mkdir(exist_ok=True)
        print("✅ Resume Processor initialized")
    
    def process_resume(self, file_path, candidate_name=None):
        """
        Process a resume file and extract text
        
        Args:
            file_path: Path to resume file (PDF, PNG, JPG, or TXT)
            candidate_name: Optional name for the candidate
        
        Returns:
            Dictionary with extracted text, metadata, and file info
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Resume file not found: {file_path}")
        
        # Validate file format
        file_ext = file_path.suffix.lower()
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        print(f"\n{'='*70}")
        print(f"📄 PROCESSING RESUME: {file_path.name}")
        print(f"{'='*70}")
        print(f"   File Type: {file_ext}")
        print(f"   File Size: {file_path.stat().st_size / 1024:.2f} KB")
        
        try:
            # Extract text based on file type
            if file_ext.lower() == '.pdf':
                extracted_text = self._extract_from_pdf(file_path)
            elif file_ext.lower() in ['.png', '.jpg', '.jpeg']:
                extracted_text = self._extract_from_image(file_path)
            elif file_ext.lower() == '.txt':
                extracted_text = self._extract_from_txt(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_ext}")
            
            # Create metadata
            if not candidate_name:
                candidate_name = file_path.stem
            
            metadata = {
                'candidate_name': candidate_name,
                'original_filename': file_path.name,
                'file_format': file_ext.lower().strip('.'),
                'file_size_kb': round(file_path.stat().st_size / 1024, 2),
                'processing_date': datetime.now().isoformat(),
                'text_length': len(extracted_text),
                'words': len(extracted_text.split())
            }
            
            result = {
                'success': True,
                'resume_text': extracted_text,
                'metadata': metadata
            }
            
            print(f"   ✅ Extracted {metadata['words']} words")
            print(f"   📝 Text Length: {metadata['text_length']} characters")
            print("="*70 + "\n")
            
            return result
        
        except Exception as e:
            print(f"   ❌ Error processing resume: {e}")
            return {
                'success': False,
                'error': str(e),
                'resume_text': ''
            }
    
    def _extract_from_pdf(self, file_path):
        """Extract text from PDF file"""
        print("   🔍 Extracting from PDF...")
        text = ""
        
        try:
            with open(file_path, 'rb') as pdf_file:
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                num_pages = len(pdf_reader.pages)
                print(f"      Pages: {num_pages}")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    print(f"      ✓ Page {page_num}/{num_pages} extracted")
            
            if not text.strip():
                raise ValueError("No text extracted from PDF")
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    def _extract_from_image(self, file_path):
        """Extract text from image using OCR (PNG, JPG)"""
        print("   🔍 Extracting from Image using OCR...")
        
        try:
            # Verify Tesseract is installed
            pytesseract.pytesseract.get_tesseract_version()
        except Exception as e:
            raise Exception(
                "Tesseract OCR not installed. "
                "Install with: sudo apt-get install tesseract-ocr (Linux) "
                "or brew install tesseract (Mac)"
            )
        
        try:
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            print(f"      Image size: {image.size}")
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            
            if not text.strip():
                raise ValueError("No text detected in image")
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Image OCR extraction failed: {str(e)}")
    
    def _extract_from_txt(self, file_path):
        """Extract text from plain text file"""
        print("   🔍 Extracting from TXT...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as txt_file:
                text = txt_file.read()
            
            if not text.strip():
                raise ValueError("Text file is empty")
            
            return text.strip()
        
        except Exception as e:
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def save_resume_metadata(self, metadata, output_name=None):
        """Save resume metadata to JSON"""
        if not output_name:
            output_name = metadata['candidate_name']
        
        metadata_file = self.resumes_dir / f"{output_name}_metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Metadata saved: {metadata_file}")
        return metadata_file
    
    def get_sample_resumes_info(self):
        """Get information about all processed resumes"""
        resumes_info = []
        
        metadata_files = self.resumes_dir.glob("*_metadata.json")
        
        for meta_file in metadata_files:
            with open(meta_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                resumes_info.append(metadata)
        
        return resumes_info