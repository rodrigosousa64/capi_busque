import os
import re
import json
import pdfplumber
from collections import defaultdict

# Paths
PDF_PATH = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\brutos\ifpa\IFPA 2026 _ TODOS OS CAMPOS.pdf"
OUTPUT_DIR = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados\novosdadosufpaqueforadobancodedados\IFPA_FINAL_FIXED"

# --- MAPPINGS ---

COURSE_KEYWORDS = {
    "ANÁLISE": "ANÁLISE E DESENVOLVIMENTO DE SISTEMAS",
    "DESENVOLVIMENTO": "ANÁLISE E DESENVOLVIMENTO DE SISTEMAS",
    "SISTEMAS": "ANÁLISE E DESENVOLVIMENTO DE SISTEMAS",
    "COMPUTAÇÃO": "CIÊNCIA DA COMPUTAÇÃO",
    "GEOGRAFIA": "GEOGRAFIA",
    "HISTÓRIA": "HISTÓRIA",
    "PEDAGOGIA": "PEDAGOGIA",
    "MATEMÁTICA": "MATEMÁTICA",
    "FÍSICA": "FÍSICA",
    "BIOLÓGICAS": "CIÊNCIAS BIOLÓGICAS",
    "AGROECO": "AGROECOLOGIA",
    "AGRONOMIA": "AGRONOMIA",
    "SANEAMENTO": "SANEAMENTO AMBIENTAL",
    "GESTÃO": "GESTÃO AMBIENTAL",
    "AMBIENTAL": "GESTÃO AMBIENTAL",
    "ELÉTRICA": "ENGENHARIA ELÉTRICA",
    "CIVIL": "ENGENHARIA CIVIL",
    "PESCA": "ENGENHARIA DE PESCA",
    "CONTROLE": "ENGENHARIA DE CONTROLE E AUTOMAÇÃO",
    "AUTOMAÇÃO": "ENGENHARIA DE CONTROLE E AUTOMAÇÃO",
    "MATERIAIS": "ENGENHARIA DE MATERIAIS",
    "LETRAS": "LETRAS",
    "PORTUGUESA": "LETRAS - LÍNGUA PORTUGUESA",
    "INGLÊS": "LETRAS - INGLÊS",
    "MÚSICA": "MÚSICA",
    "ARTES": "ARTES VISUAIS",
}

CAMPUS_KEYWORDS = {
    "ABAETETUBA": "ABAETETUBA",
    "ALTAMIRA": "ALTAMIRA",
    "ANANINDEUA": "ANANINDEUA",
    "BELÉM": "BELÉM",
    "BRAGANÇA": "BRAGANÇA",
    "CASTANHAL": "CASTANHAL",
    "ITAITUBA": "ITAITUBA",
    "MARABÁ": "MARABÁ",
    "ÓBIDOS": "ÓBIDOS",
    "PARAGOMINAS": "PARAGOMINAS",
    "SANTARÉM": "SANTARÉM",
    "TUCURUÍ": "TUCURUÍ",
    "PARAUAPEBAS": "PARAUAPEBAS",
    "TUCURUI": "TUCURUÍ",
}

def detect_metadata(text):
    # Flexible match for keywords
    text_clean = text.upper().replace(" ", "")
    
    found_course = None
    for kw, full_name in COURSE_KEYWORDS.items():
        if kw in text_clean:
            found_course = full_name
            break
            
    found_campus = None
    for kw, full_name in CAMPUS_KEYWORDS.items():
        if kw in text_clean:
            found_campus = full_name
            break
            
    found_degree = "GRADUAÇÃO"
    if "LICENCIATURA" in text_clean: found_degree = "LICENCIATURA"
    elif "BACHARELADO" in text_clean: found_degree = "BACHARELADO"
    elif "TECNOLOGIA" in text_clean: found_degree = "TECNOLOGIA"
    
    found_shift = None
    if "VESPERTINO" in text_clean: found_shift = "VESPERTINO"
    elif "NOTURNO" in text_clean: found_shift = "NOTURNO"
    elif "MATUTINO" in text_clean: found_shift = "MATUTINO"
    elif "INTEGRAL" in text_clean: found_shift = "INTEGRAL"
    
    return found_course, found_campus, found_degree, found_shift

# --- REUSE MAPPINGS ---
from process_ifpa_2026_final import QUOTA_DESCRIPTIONS, A_MAP
QUOTAS = ["RI_PPI", "RI_Q", "RI_PCD", "RI_EP", "IR_PPI", "IR_Q", "IR_PCD", "IR_EP", "AC"]

def process_ifpa_2026():
    print(f"Starting Final Fixed Extraction from {PDF_PATH}...")
    offerings = defaultdict(list)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        state = {"course": None, "campus": None, "degree": "GRADUAÇÃO", "shift": None}
        
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text: continue
            
            # Use whole page text for metadata because it's often split across lines
            c, camp, d, s = detect_metadata(text)
            if c: state["course"] = c
            if camp: state["campus"] = camp
            if d != "GRADUAÇÃO": state["degree"] = d
            if s: state["shift"] = s
            
            lines = text.split("\n")
            for line in lines:
                # If we see 'Graduação -', prioritize the course in that line
                if "Graduação" in line:
                    c_line, _, d_line, s_line = detect_metadata(line)
                    if c_line: state["course"] = c_line
                    if d_line != "GRADUAÇÃO": state["degree"] = d_line
                    if s_line: state["shift"] = s_line

                if "Aprovado(a)" in line or "Classificado(a)" in line:
                    parts = line.split()
                    status_idx = -1
                    for idx, p in enumerate(parts):
                        if "Aprovado(a)" in p or "Classificado(a)" in p:
                            status_idx = idx
                            break
                    
                    if status_idx != -1 and status_idx >= 3:
                        try:
                            score = float(parts[status_idx - 3].replace(",", "."))
                            applied_q = parts[status_idx - 2]
                            class_q = parts[status_idx + 1] if status_idx + 1 < len(parts) else None
                            
                            final_q = class_q if class_q in QUOTAS else applied_q
                            if final_q not in QUOTAS:
                                final_q = A_MAP.get(final_q, applied_q)
                                if final_q not in QUOTAS: final_q = "AC"
                            
                            if state["course"] and state["campus"] and state["shift"]:
                                key = (state["campus"], state["course"], state["degree"], state["shift"])
                                offerings[key].append({"score": score, "quota": final_q})
                        except: pass
            
            if i % 10 == 0:
                print(f"Page {i+1}/60: {state['course']} ({state['campus']}) - {state['shift']}")

    # --- SAVE ---
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    for (campus, course, degree, shift), candidates in offerings.items():
        if not candidates: continue
        quota_groups = defaultdict(list)
        for cand in candidates: quota_groups[cand["quota"]].append(cand["score"])
        
        comp_data = []
        total_spots = 0
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
        
        def slug(t): return str(t).lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ç", "c")
        fn = f"ifpa_{slug(course)}_{slug(campus)}_{slug(degree)}_{slug(shift)}_2026.json"
        with open(os.path.join(OUTPUT_DIR, fn), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"Saved: {fn}")

if __name__ == "__main__":
    process_ifpa_2026()
