import os
import pymupdf
import pytesseract
from PIL import Image
import io

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

pdf_path = r'C:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\brutos\ufpa\newdatas\Altamira\011_GEOGRAFIA_LIC_EXT_MATUTINO_ENTRADA_1.pdf'

def test_ocr():
    print(f"Lendo {pdf_path}...")
    doc = pymupdf.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(dpi=300)
    img_data = pix.tobytes("png")
    img = Image.open(io.BytesIO(img_data))
    
    # Roda OCR sem especificar lingua
    text = pytesseract.image_to_string(img)
    
    print("----- OCR TEXT -----")
    print(text[:1000])
    print("--------------------")

if __name__ == "__main__":
    test_ocr()
