import pdfplumber

pdf_path = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\brutos\ifpa\IFPA 2026 _ TODOS OS CAMPOS.pdf"

with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[10] # Page 11
    print(page.extract_text())
