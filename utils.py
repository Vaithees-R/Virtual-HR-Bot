# utils.py
import os
import fitz  # This is PyMuPDF
import pytesseract
from PIL import Image
from werkzeug.utils import secure_filename
from config import UPLOADS_DIR, ALLOWED_EXTENSIONS
from pathlib import Path

# --- Tesseract Configuration ---
# If you installed Tesseract in a custom location on Windows, you might
# need to uncomment the line below and set the correct path.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_resume_file(file_storage) -> str:
    """
    Saves and extracts text from an uploaded resume file (PDF, PNG, JPG, TXT).
    Returns the extracted text as a string.
    """
    if not file_storage or not allowed_file(file_storage.filename):
        raise ValueError("Invalid file type. Allowed: " + ", ".join(ALLOWED_EXTENSIONS))

    filename = secure_filename(file_storage.filename)
    filepath = UPLOADS_DIR / filename
    
    # Save the file temporarily
    file_storage.save(filepath)

    text = ""
    ext = filename.rsplit('.', 1)[1].lower()

    try:
        if ext == 'pdf':
            with fitz.open(filepath) as doc:
                for page in doc:
                    text += page.get_text()
            print(f"✅ Extracted text from PDF: {filename}")
        
        elif ext in {'png', 'jpg', 'jpeg'}:
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img)
            print(f"✅ Extracted text from Image (OCR): {filename}")
        
        elif ext == 'txt':
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            print(f"✅ Extracted text from TXT: {filename}")
        
        if not text:
            raise ValueError(f"Could not extract any text from {filename}. File might be empty or corrupted.")
            
        return text
    
    except Exception as e:
        print(f"❌ Error processing file {filename}: {e}")
        # Try to provide a helpful Tesseract error
        if 'tesseract is not installed' in str(e).lower():
             raise RuntimeError(
                "Tesseract-OCR not found. "
                "Please install it on your system to process images. "
                "See: https://github.com/UB-Mannheim/tesseract/wiki"
            )
        raise
    
    finally:
        # Clean up the uploaded file after processing
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"⚠️ Warning: Could not delete temp file {filepath}: {e}")