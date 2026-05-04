import pdfplumber
import os

pdf_path = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\brutos\ifpa\IFPA 2026 _ TODOS OS CAMPOS.pdf"

with pdfplumber.open(pdf_path) as pdf:
    full_text = ""
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            full_text += f"--- Page {i+1} ---\n{text}\n"
        if i > 5: break # Just first 6 pages
    
    with open(r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\scratch\ifpa_extracted.txt", "w", encoding="utf-8") as f:
        f.write(full_text)

print("Extraction complete. Check scratch/ifpa_extracted.txt")
