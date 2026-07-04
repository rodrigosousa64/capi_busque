import os
import re
import json
import pdfplumber
from collections import defaultdict

# Paths
PDF_PATH = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\brutos\ifpa\IFPA 2026 _ TODOS OS CAMPOS.pdf"
OUTPUT_DIR = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados\novosdadosufpaqueforadobancodedados\IFPA_FIXED"

QUOTA_DESCRIPTIONS = {
    "RI_PPI": "Vagas reservadas a candidatos autodeclarados pretos, pardos ou indígenas, com renda familiar bruta igual ou inferior a 1 salário mínimo per capita, que tenham cursado o ensino médio integralmente em escola pública.",
    "RI_Q": "Vagas reservadas a candidatos autodeclarados quilombolas com renda familiar bruta per capita igual ou inferior a 1 salário mínimo, que tenham cursado o ensino médio integralmente em escola pública.",
    "RI_PCD": "Vagas reservadas a candidatos com deficiência, com renda familiar bruta igual ou inferior a 1 salário mínimo per capita, que tenham cursado o ensino médio integralmente em escola pública.",
    "RI_EP": "Vagas reservadas a candidatos com renda familiar bruta per capita igual ou inferior a 1 salário mínimo, que tenham cursado o ensino médio integralmente em escola pública (Geral/Independente de autodeclaração).",
    "IR_PPI": "Vagas reservadas a candidatos autodeclarados pretos, pardos ou indígenas, independente de renda, que tenham cursado o ensino médio integralmente em escola pública.",
    "IR_Q": "Vagas reservadas a candidatos autodeclarados quilombolas, independente de renda, que tenham cursado o ensino médio integralmente em escola pública.",
    "IR_PCD": "Vagas reservadas a candidatos com deficiência, independente de renda, que tenham cursado o ensino médio integralmente em escola pública.",
    "IR_EP": "Vagas reservadas a candidatos, independente de renda, que tenham cursado o ensino médio integralmente em escola pública (Geral/Independente de autodeclaração).",
    "AC": "Ampla Concorrência"
}

A_MAP = {
    "A01": "RI_PCD", "A02": "RI_PPI", "A03": "RI_Q", "A04": "RI_EP",
    "A05": "RI_PPI", "A06": "IR_PCD", "A07": "IR_PPI", "A09": "IR_Q",
    "A11": "RI_EP", "A12": "IR_PPI", "A13": "IR_EP", "A15": "RI_PPI",
    "A19": "IR_PPI",
}

COURSE_FIXES = {
    "CIÊNCIA DA": "CIÊNCIA DA COMPUTAÇÃO",
    "ANÁLISE E": "ANÁLISE E DESENVOLVIMENTO DE SISTEMAS",
    "GESTÃO": "GESTÃO AMBIENTAL",
    "SANEAMENTO": "SANEAMENTO AMBIENTAL",
    "AGROECO": "AGROECOLOGIA",
    "LÍNGUA PORTUGUESA": "LETRAS - LÍNGUA PORTUGUESA",
    "LETRAS - PORTUGUESA": "LETRAS - LÍNGUA PORTUGUESA",
    "HISTÓRIA": "HISTÓRIA",
    "GEOGRAFIA": "GEOGRAFIA",
    "MATEMÁTICA": "MATEMÁTICA",
    "PEDAGOGIA": "PEDAGOGIA",
    "FÍSICA": "FÍSICA",
    "CIÊNCIAS": "CIÊNCIAS BIOLÓGICAS",
}

CAMPUS_LIST = ["ABAETETUBA", "ALTAMIRA", "ANANINDEUA", "BELÉM", "BRAGANÇA", "CASTANHAL", "ITAITUBA", "MARABÁ", "ÓBIDOS", "PARAGOMINAS", "SANTARÉM", "TUCURUÍ", "VIGIA", "BREVES", "CAMETÁ", "CAPANEMA", "CONCEIÇÃO DO ARAGUAIA", "ITAITUBA", "MARABÁ INDUSTRIAL", "PARAUAPEBAS", "SANTARÉM", "TUCURUÍ"]

def fix_course(name):
    name = name.upper().strip()
    for key, value in COURSE_FIXES.items():
        if name.startswith(key):
            return value
    return name

def extract_campus_and_degree(line):
    line_upper = line.upper()
    campus = "UNKNOWN"
    degree = "GRADUAÇÃO"
    
    for c in CAMPUS_LIST:
        if c in line_upper:
            campus = c
            break
            
    if "LICENCIATURA" in line_upper or "L I C E N C I A T U R A" in line_upper:
        degree = "LICENCIATURA"
    elif "BACHARELADO" in line_upper or "B A C H A R E L A D O" in line_upper:
        degree = "BACHARELADO"
    elif "TECNOLOGIA" in line_upper or "T E C N O L O G I A" in line_upper:
        degree = "TECNOLOGIA"
        
    return campus, degree

def normalize_quota(code, applied_code=None):
    if not code or code == "-": return None
    code = code.strip().upper().replace("-", "_")
    if code in QUOTA_DESCRIPTIONS: return code
    if code in A_MAP: return A_MAP[code]
    if applied_code:
        applied_code = applied_code.strip().upper().replace("-", "_")
        if applied_code in QUOTA_DESCRIPTIONS: return applied_code
    return None

def slugify(text):
    import unicodedata
    if not text: return "na"
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '_', text)

def process_ifpa_2026():
    print(f"Opening {PDF_PATH}...")
    # Key: (Campus, Course, Degree, Shift)
    offerings_data = defaultdict(list)
    
    with pdfplumber.open(PDF_PATH) as pdf:
        current_course = None
        current_campus = "UNKNOWN"
        current_degree = "GRADUAÇÃO"
        current_shift = "N/A"
        
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text: continue
            
            lines = text.split("\n")
            for line in lines:
                # Course Detection
                if "Graduação" in line and "-" in line:
                    parts = line.split("-")
                    if len(parts) >= 2:
                        course_part = parts[1].strip()
                        if course_part:
                            current_course = fix_course(course_part)
                
                # Campus and Degree Detection
                if "Campus" in line:
                    campus, degree = extract_campus_and_degree(line)
                    if campus != "UNKNOWN":
                        current_campus = campus
                    if degree != "GRADUAÇÃO":
                        current_degree = degree

                # Shift Detection
                if "Turno" in line or "T a u m rn p o u" in line:
                    if "Vespertino" in line: current_shift = "VESPERTINO"
                    elif "Noturno" in line: current_shift = "NOTURNO"
                    elif "Matutino" in line: current_shift = "MATUTINO"
                    elif "Integral" in line: current_shift = "INTEGRAL"

                # Candidate Detection
                if "Aprovado(a)" in line or "Classificado(a)" in line:
                    parts = line.split()
                    status_idx = -1
                    for idx, p in enumerate(parts):
                        if "Aprovado(a)" in p or "Classificado(a)" in p:
                            status_idx = idx
                            break
                    
                    if status_idx != -1 and status_idx >= 3:
                        classified_quota = parts[status_idx + 1] if status_idx + 1 < len(parts) else None
                        applied_quota = parts[status_idx - 2]
                        score_str = parts[status_idx - 3]
                        
                        try:
                            score = float(score_str.replace(",", "."))
                            norm_quota = normalize_quota(classified_quota, applied_quota)
                            
                            if norm_quota and current_course:
                                key = (current_campus, current_course, current_degree, current_shift)
                                offerings_data[key].append({
                                    "score": score,
                                    "quota": norm_quota
                                })
                        except: pass

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    for (campus, course, degree, shift), candidates in offerings_data.items():
        if not candidates: continue
        
        quota_groups = defaultdict(list)
        for c in candidates: quota_groups[c["quota"]].append(c["score"])
        
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
                "course": course.upper(), "campus": campus.upper(),
                "degree": degree.upper(), "shift": shift,
                "total_spots_filled": total_spots, "leftover_spots": 0,
                "competition_data": comp_data
            }]
        }
        fn = f"ifpa_{slugify(course)}_{slugify(campus)}_{slugify(degree)}_{slugify(shift)}_2026.json"
        with open(os.path.join(OUTPUT_DIR, fn), "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print(f"Saved {fn}")

if __name__ == "__main__":
    process_ifpa_2026()
