import pdfplumber
import re
from collections import Counter

pdf_path = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\brutos\ifpa\IFPA 2026 _ TODOS OS CAMPOS.pdf"

vagas_classificacao = Counter()

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if not text: continue
        
        # Look for the last part of the line which is the classification group
        # Pattern: [Status] [Group]
        # Example: Aprovado(a) AC
        # Example: Classificado(a) IR_EP
        matches = re.findall(r"(?:Aprovado\(a\)|Classificado\(a\))\s+([A-Z0-9_ -]+)", text)
        for m in matches:
            vagas_classificacao[m.strip()] += 1
        
        if i > 50: break # Check first 50 pages

print(vagas_classificacao)
