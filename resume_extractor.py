"""
resume_extractor.py
Handles text extraction from resume files (PDF, DOCX, or Image)
"""

import os
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
from docx import Document

# Path to Tesseract (update this for your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_from_pdf(file_path: str) -> str:
    """Extract text from PDF resumes"""
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() or ""
    except Exception as e:
        print(f"⚠️ PDF extraction error: {e}")
    return text.strip()

def extract_from_docx(file_path: str) -> str:
    """Extract text from Word documents"""
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"⚠️ DOCX extraction error: {e}")
    return text.strip()

def extract_from_image(file_path: str) -> str:
    """Extract text from image-based resumes using OCR"""
    text = ""
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
    except Exception as e:
        print(f"⚠️ Image extraction error: {e}")
    return text.strip()

def extract_resume_text(file_path: str) -> str:
    """Main function to detect file type and extract text"""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return extract_from_pdf(file_path)
    elif ext in [".jpg", ".jpeg", ".png"]:
        return extract_from_image(file_path)
    elif ext in [".docx"]:
        return extract_from_docx(file_path)
    else:
        raise ValueError("Unsupported file type! Please upload PDF, DOCX, or image.")

if __name__ == "__main__":
    test_path = "D:\Documents\OIP-1056857393.jpg"  # test any file here
    content = extract_resume_text(test_path)
    print("\n🧠 Extracted Resume Content:\n")
    print(content[:1000])  # preview first 1000 chars
