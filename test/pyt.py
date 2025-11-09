import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image
import pytesseract

text = pytesseract.image_to_string(Image.open("D:\Documents\OIP-1056857393.jpg"))
print(text[:300])
