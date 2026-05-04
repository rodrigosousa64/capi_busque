import os
import re
import json
import pdfplumber
from collections import Counter

# Paths
BRUTOS_DIR = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\brutos\ufpa"
OUTPUT_DIR = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados\novosdadosufpaqueforadobancodedados"

# Quota Mapping (Old PDF Code -> New User Code)
QUOTA_MAPPING = {
    "AC": "AC",
    "ER": "RI_EP",
    "ERPPI": "RI_PPI",
    "ERQ": "RI_Q",
    "ERPCD": "RI_PCD",
    "E": "IR_EP",
    "EPPI": "IR_PPI",
    "EQ": "IR_Q",
    "EPCD": "IR_PCD",
    "PCDA": "IR_PCD" # Mapping PCDA to IR_PCD as it's independent of income and PCD
}

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

def clean_name(name):
    # Handle the +® encoding issue
    return name.replace("+®", "é").replace("+®", "é").replace("+¡", "á").replace("+¡", "á").replace("+¦", "í").replace("+¦", "í").replace("+ó", "ó").replace("+║", "ú")

def process_pdf(pdf_path):
    print(f"Processing {pdf_path}...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return None

    lines = full_text.split("\n")
    
    # Extract metadata
    course = ""
    campus = ""
    shift = ""
    year = 2026
    total_spots_filled = 0
    
    for line in lines:
        if "Curso:" in line:
            # Match: Curso: ADMINISTRACAO (BAC/EXT/MATUTINO/ENTRADA 1)
            match = re.search(r"Curso:\s*(.*?)\s*\((.*?)\)", line)
            if match:
                course = match.group(1).strip()
                info_parts = match.group(2).split("/")
                # Extract shift - look for keywords
                for part in info_parts:
                    if "MATUTINO" in part: shift = "MATUTINO"
                    elif "VESPERTINO" in part: shift = "VESPERTINO"
                    elif "NOTURNO" in part: shift = "NOTURNO"
                    elif "INTEGRAL" in part: shift = "INTEGRAL"
        
        if "Cidade:" in line:
            campus = line.replace("Cidade:", "").strip()
        
        if "Vagas Preenchidas:" in line:
            try:
                total_spots_filled = int(re.search(r"Vagas Preenchidas:\s*(\d+)", line).group(1))
            except: pass

    # Extract candidate list to count spots per quota
    quota_counts = Counter()
    # Looking for lines like: ABRAAO PINHEIRO SANCHES 156381 AC 683.6 12ª (AC) ...
    # We look for the quota code in the pattern (CODE) or after the score
    for line in lines:
        match = re.search(r"\(\b(AC|PCDA|E|EPCD|EQ|EPPI|ER|ERPCD|ERQ|ERPPI)\b\)", line)
        if match:
            quota_counts[match.group(1)] += 1
        elif "AC" in line or "PCDA" in line or "ERPPI" in line: # Fallback for lines without parens but with code
            # Only if it looks like a candidate line (name + number + code + score)
            if re.search(r"\d{5,}\s+(AC|PCDA|E|EPCD|EQ|EPPI|ER|ERPCD|ERQ|ERPPI)\s+\d+", line):
                code = re.search(r"\s+(AC|PCDA|E|EPCD|EQ|EPPI|ER|ERPCD|ERQ|ERPPI)\s+", line).group(1)
                quota_counts[code] += 1

    # Extract Max/Min table
    max_scores = {}
    min_scores = {}
    
    table_header_idx = -1
    for i, line in enumerate(lines):
        if "Notas Máximas e Mínimas" in line:
            table_header_idx = i + 1
            break
    
    if table_header_idx != -1 and table_header_idx + 2 < len(lines):
        headers = lines[table_header_idx].split()
        max_vals = lines[table_header_idx+1].replace("Máximas", "").strip().split()
        min_vals = lines[table_header_idx+2].replace("Mínimas", "").strip().split()
        
        # Sometimes there's a "-" if no one classified
        for i, h in enumerate(headers):
            if i < len(max_vals) and max_vals[i] != "-":
                try:
                    max_scores[h] = float(max_vals[i])
                except: pass
            if i < len(min_vals) and min_vals[i] != "-":
                try:
                    min_scores[h] = float(min_vals[i])
                except: pass

    # Map to new structure
    new_competition_data = {}
    
    # Initialize all 9 categories
    for code in QUOTA_DESCRIPTIONS.keys():
        new_competition_data[code] = {
            "quota_code": code,
            "description": QUOTA_DESCRIPTIONS[code],
            "spots": 0,
            "previous_cutoff": 0.0,
            "historical_max_score": 0.0
        }
    
    # Fill from PDF data
    # Note: Multiple old codes might map to one new code (e.g. EPCD and ERPCD both map to PCD variants)
    # Actually, the mapping is 1-to-1 except for PCDA.
    # Let's handle it carefully.
    
    for old_code, count in quota_counts.items():
        new_code = QUOTA_MAPPING.get(old_code)
        if new_code:
            target = new_competition_data[new_code]
            target["spots"] += count
            
            # For min/max, we take the overall min/max if multiple old codes map to one new code
            p_max = max_scores.get(old_code, 0.0)
            p_min = min_scores.get(old_code, 0.0)
            
            if p_max > target["historical_max_score"]:
                target["historical_max_score"] = p_max
            
            if target["previous_cutoff"] == 0.0 or (p_min < target["previous_cutoff"] and p_min > 0):
                target["previous_cutoff"] = p_min
            # Wait, cutoff should be the minimum score of that group.
            # If multiple groups map to one, we take the overall minimum? 
            # Actually, the user's logic split them by income. 
            # EPPI (Old) -> IR_PPI (New)
            # ERPPI (Old) -> RI_PPI (New)
            # These are 1-to-1. Only PCDA might overlap.
            # Let's re-verify.

    # Format result
    result = {
        "institution": "UFPA",
        "year_reference": 2026,
        "offerings": [
            {
                "course": course,
                "campus": campus,
                "degree": "BAC", # Defaulting to BAC as seen in sample
                "shift": shift,
                "total_spots_filled": total_spots_filled,
                "leftover_spots": 0,
                "competition_data": list(new_competition_data.values())
            }
        ]
    }
    
    return result

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    for filename in os.listdir(BRUTOS_DIR):
        if filename.endswith(".pdf") and "2026" in filename:
            pdf_path = os.path.join(BRUTOS_DIR, filename)
            data = process_pdf(pdf_path)
            if data:
                # Create output filename
                clean_fn = clean_name(filename).lower().replace(".pdf", ".json")
                # Remove 'ufpa_' prefix and normalize
                clean_fn = clean_fn.replace("ufpa_", "")
                output_path = os.path.join(OUTPUT_DIR, clean_fn)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                print(f"Saved to {output_path}")

if __name__ == "__main__":
    main()
