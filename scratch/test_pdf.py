import pdfplumber
import os

pdf_path = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\brutos\ufpa\ufpa_administracao_matutino_bel+®m_2026.pdf"

with pdfplumber.open(pdf_path) as pdf:
    full_text = ""
    for page in pdf.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
    
    with open(r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\scratch\extracted_text.txt", "w", encoding="utf-8") as f:
        f.write(full_text)

print("Extraction complete. Check scratch/extracted_text.txt")
