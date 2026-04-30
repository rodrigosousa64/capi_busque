import pdfplumber

pdf_path = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\Verificador-de-notas-de-cursos-max-e-min-das-universidades-federias-metropolinas-de-bel-m-\dados_de-cursos\UFRA_BY_SISU\CONVOCACAO_CR_SISU_2026.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            # check for shifts
            shifts = ["MATUTINO", "VESPERTINO", "NOTURNO", "INTEGRAL"]
            for s in shifts:
                if s in text.upper():
                    print(f"Found {s} on page {i+1}")
                    
        # Let's also print the very first few lines of the first page to see what's there
        if i == 0:
            print("--- First page raw text ---")
            print(text[:500])
