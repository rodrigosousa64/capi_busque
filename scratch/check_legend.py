import pdfplumber

pdf_path = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\brutos\ifpa\IFPA 2026 _ TODOS OS CAMPOS.pdf"

with pdfplumber.open(pdf_path) as pdf:
    last_page = pdf.pages[-1]
    text = last_page.extract_text()
    print(text)
