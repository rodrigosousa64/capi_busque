import os
import re
import json
import pdfplumber
from collections import defaultdict

# Paths
PDF_PATH = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\brutos\ifpa\IFPA 2026 _ TODOS OS CAMPOS.pdf"
OUTPUT_DIR = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados\novosdadosufpaqueforadobancodedados\IFPA_CORRIGIDO"

# --- DEFINITIONS ---

COURSES = [
    "ANÁLISE E DESENVOLVIMENTO DE SISTEMAS",
    "CIÊNCIA DA COMPUTAÇÃO",
    "GESTÃO AMBIENTAL",
    "SANEAMENTO AMBIENTAL",
    "AGROECOLOGIA",
    "AGRONOMIA",
    "ENGENHARIA CIVIL",
    "ENGENHARIA DE CONTROLE E AUTOMAÇÃO",
    "ENGENHARIA DE MATERIAIS",
    "ENGENHARIA DE PESCA",
    "ENGENHARIA ELÉTRICA",
    "GEOGRAFIA",
    "HISTÓRIA",
    "LETRAS - LÍNGUA PORTUGUESA",
    "LETRAS - INGLÊS",
    "MATEMÁTICA",
    "PEDAGOGIA",
    "FÍSICA",
    "CIÊNCIAS BIOLÓGICAS",
    "MÚSICA",
    "EDUCAÇÃO FÍSICA",
    "ARTES VISUAIS",
    "ELETROTÉCNICA INDUSTRIAL",
]

CAMPUSES = [
    "ABAETETUBA", "ALTAMIRA", "ANANINDEUA", "BELÉM", "BRAGANÇA", 
    "CASTANHAL", "ITAITUBA", "MARABÁ", "ÓBIDOS", "PARAGOMINAS", 
    "SANTARÉM", "TUCURUÍ", "VIGIA", "BREVES", "CAMETÁ", "CAPANEMA", 
    "CONCEIÇÃO DO ARAGUAIA", "PARAUAPEBAS"
]

QUOTAS = ["RI_PPI", "RI_Q", "RI_PCD", "RI_EP", "IR_PPI", "IR_Q", "IR_PCD", "IR_EP", "AC"]

# --- PARSING LOGIC ---

def get_best_match(text, options):
    for opt in options:
        # Create a pattern that allows spaces between characters
        pattern = "".join([re.escape(c) + r"\s*" for c in opt])
        if re.search(pattern, text, re.IGNORECASE):
            return opt
    return None

def process_ifpa_2026():
    print(f"Starting precise extraction from {PDF_PATH}...")
    offerings = defaultdict(list)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        curr_course = None
        curr_campus = None
        curr_degree = "GRADUAÇÃO"
        curr_shift = None
        
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text: continue
            
            lines = text.split("\n")
            
            # 1. Scan page for new metadata
            # We look for metadata in the whole page text because it's often fragmented
            found_course = get_best_match(text, COURSES)
            found_campus = get_best_match(text, CAMPUSES)
            
            if found_course: curr_course = found_course
            if found_campus: curr_campus = found_campus
            
            # Degree detection
            if get_best_match(text, ["LICENCIATURA"]): curr_degree = "LICENCIATURA"
            elif get_best_match(text, ["BACHARELADO"]): curr_degree = "BACHARELADO"
            elif get_best_match(text, ["TECNOLOGIA"]): curr_degree = "TECNOLOGIA"
            
            # Shift detection
            found_shift = get_best_match(text, ["VESPERTINO", "NOTURNO", "MATUTINO", "INTEGRAL"])
            if found_shift: curr_shift = found_shift

            # 2. Process Candidates
            for line in lines:
                # If we see a new 'Graduação -', it's a strong signal of a course change
                if "Graduação -" in line:
                    new_course = get_best_match(line, COURSES)
                    if new_course: curr_course = new_course
                
                if "Aprovado(a)" in line or "Classificado(a)" in line:
                    # Logic to extract score and quota
                    parts = line.split()
                    status_idx = -1
                    for idx, p in enumerate(parts):
                        if "Aprovado(a)" in p or "Classificado(a)" in p:
                            status_idx = idx
                            break
                    
                    if status_idx != -1 and status_idx >= 3:
                        score_str = parts[status_idx - 3]
                        applied_q = parts[status_idx - 2]
                        class_q = parts[status_idx + 1] if status_idx + 1 < len(parts) else None
                        
                        try:
                            score = float(score_str.replace(",", "."))
                            # Use classified quota if available, otherwise applied
                            final_q = class_q if class_q in QUOTAS else applied_q
                            if final_q not in QUOTAS: # Handle Axx codes
                                from process_ifpa_2026_final import A_MAP
                                final_q = A_MAP.get(final_q, applied_q)
                                if final_q not in QUOTAS: final_q = "AC"

                            if curr_course and curr_campus and curr_shift:
                                key = (curr_campus, curr_course, curr_degree, curr_shift)
                                offerings[key].append({"score": score, "quota": final_q})
                        except: pass
            
            if i % 10 == 0:
                print(f"Page {i+1}/60: {curr_course} | {curr_campus} | {curr_shift}")

    # 3. Save JSONs
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    for (campus, course, degree, shift), candidates in offerings.items():
        quota_groups = defaultdict(list)
        for c in candidates: quota_groups[c["quota"]].append(c["score"])
        
        comp_data = []
        total_spots = 0
        from process_ifpa_2026_final import QUOTA_DESCRIPTIONS
        for q_code, desc in QUOTA_DESCRIPTIONS.items():
            scores = quota_groups.get(q_code, [])
            spots = len(scores)
            total_spots += spots
            comp_data.append({
                "quota_code": q_code, "description": desc, "spots": spots,
                "previous_cutoff": min(scores) if scores else 0.0,
                "historical_max_score": max(scores) if scores else 0.0
            })
            
        result = {
            "institution": "IFPA", "year_reference": 2026,
            "offerings": [{
                "course": course, "campus": campus, "degree": degree, "shift": shift,
                "total_spots_filled": total_spots, "leftover_spots": 0, "competition_data": comp_data
            }]
        }
        
        def slug(t): return str(t).lower().replace(" ", "_").replace("Á", "a").replace("É", "e").replace("Í", "i").replace("Ó", "o").replace("Ú", "u").replace("Ç", "c")
        fn = f"ifpa_{slug(course)}_{slug(campus)}_{slug(degree)}_{slug(shift)}_2026.json"
        with open(os.path.join(OUTPUT_DIR, fn), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"Saved: {fn}")

if __name__ == "__main__":
    process_ifpa_2026()
