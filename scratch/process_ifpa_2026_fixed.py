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

# Known mappings for fragmented course names in IFPA PDF
COURSE_FIXES = {
    "CIÊNCIA DA": "CIÊNCIA DA COMPUTAÇÃO",
    "ANÁLISE E": "ANÁLISE E DESENVOLVIMENTO DE SISTEMAS",
    "GESTÃO": "GESTÃO AMBIENTAL",
    "SANEAMENTO": "SANEAMENTO AMBIENTAL",
    "AGROECO": "AGROECOLOGIA",
    "LÍNGUA PORTUGUESA": "LETRAS - LÍNGUA PORTUGUESA",
    "ENGENHARIA": "ENGENHARIA", # Generic fallback, will try to improve
}

CAMPUS_FIXES = {
    "ANANINDEUA BACHARELADO": "ANANINDEUA",
    "ALTAMIRA SISTEMAS": "ALTAMIRA",
    "ABAETETUBA LICENCIATURA": "ABAETETUBA",
    "BELEM SISTEMAS": "BELÉM",
    "BRAGANCA": "BRAGANÇA",
}

def fix_course(name):
    name = name.upper().strip()
    for key, value in COURSE_FIXES.items():
        if name.startswith(key):
            return value
    return name

def fix_campus(name):
    name = name.upper().strip()
    for key, value in CAMPUS_FIXES.items():
        if name.startswith(key):
            return value
    return name

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
    courses_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    with pdfplumber.open(PDF_PATH) as pdf:
        current_course = None
        current_campus = None
        current_shift = None
        
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text: continue
            
            lines = text.split("\n")
            for line in lines:
                # Better Header Detection
                if "Graduação" in line and "-" in line:
                    parts = line.split("-")
                    if len(parts) >= 2:
                        course_part = parts[1].strip()
                        if course_part:
                            current_course = fix_course(course_part)
                
                if "Campus" in line:
                    campus_match = re.search(r"Campus\s+([\w\s]+)", line)
                    if campus_match:
                        campus_name = campus_match.group(1).strip()
                        if len(campus_name) < 40:
                            current_campus = fix_campus(campus_name)

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
                            
                            course = current_course if current_course else "UNKNOWN"
                            campus = current_campus if current_campus else "UNKNOWN"
                            shift = current_shift if current_shift else "N/A"
                            
                            if norm_quota:
                                courses_data[campus][course][shift].append({
                                    "score": score,
                                    "quota": norm_quota
                                })
                        except: pass

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    for campus, courses in courses_data.items():
        for course_name, shifts in courses.items():
            for shift, candidates in shifts.items():
                if not candidates or course_name == "UNKNOWN": continue
                
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
                        "course": course_name.upper(), "campus": campus.upper(),
                        "degree": "GRADUAÇÃO", "shift": shift,
                        "total_spots_filled": total_spots, "leftover_spots": 0,
                        "competition_data": comp_data
                    }]
                }
                fn = f"ifpa_{slugify(course_name)}_{slugify(campus)}_{slugify(shift)}_2026.json"
                with open(os.path.join(OUTPUT_DIR, fn), "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                print(f"Saved {fn}")

if __name__ == "__main__":
    process_ifpa_2026()
