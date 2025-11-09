
from PyPDF2 import PdfReader
reader = PdfReader("D:\Documents\Abstract Form - Vaithees R - 2.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()
print(text[:300])
