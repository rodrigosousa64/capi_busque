import glob
import re
import pdfplumber

pdfs = glob.glob('pipeline_dados/brutos/ufpa/*.pdf')
sobras = []

for pdf_path in pdfs:
    with pdfplumber.open(pdf_path) as pdf:
        text = pdf.pages[0].extract_text()
        if not text: continue
        
        curso, cidade = '', ''
        vagas_of, vagas_pr = 0, 0
        
        for line in text.split('\n'):
            if line.startswith('Cidade:'): 
                cidade = line.replace('Cidade:','').strip()
            elif line.startswith('Curso:'): 
                curso = line.replace('Curso:','').strip()
            elif line.startswith('Vagas Ofertadas:'):
                vagas_of_str = line.replace('Vagas Ofertadas:','').strip()
                # "45 + 1 PCD" -> [45, 1] -> 46
                nums = re.findall(r'\d+', vagas_of_str)
                vagas_of = sum(int(x) for x in nums)
            elif line.startswith('Vagas Preenchidas:'):
                match = re.search(r'\d+', line)
                if match:
                    vagas_pr = int(match.group())
        
        if vagas_of > vagas_pr:
            sobras.append({
                'cidade': cidade, 
                'curso': curso, 
                'ofertadas': vagas_of, 
                'preenchidas': vagas_pr, 
                'sobra': vagas_of - vagas_pr
            })

if not sobras:
    print("Nenhuma sobra de vagas encontrada na UFPA.")
else:
    print("SOBRAS ENCONTRADAS NA UFPA:")
    for s in sobras:
        print(f"- {s['cidade']} | {s['curso']}: Sobraram {s['sobra']} vagas (Ofertadas: {s['ofertadas']}, Preenchidas: {s['preenchidas']})")
