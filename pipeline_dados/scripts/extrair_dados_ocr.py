import os
import glob
import re
import sys
import json
import pymupdf
import pytesseract
from PIL import Image
import io

scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from extrair_pdf import normalizar_nome_arquivo, PASTA_DESTINO

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def parse_course_info(course_line, campus_line):
    campus = campus_line.replace("Cidade:", "").strip().title()
    course_raw = course_line.replace("Curso:", "").strip()
    match = re.match(r'^(.+?)\s*\((.+?)\)', course_raw)
    
    if not match:
        return course_raw, campus, "Não Informado"
        
    course_name = match.group(1).strip()
    details = match.group(2).strip().split('/')
    
    shift = "Não Informado"
    for p in details:
        p_clean = p.strip().upper()
        if p_clean in ['MATUTINO', 'VESPERTINO', 'NOTURNO', 'INTEGRAL']:
            shift = p_clean.capitalize()
            break
            
    return course_name, campus, shift

def process_pdf(pdf_path):
    print(f"Lendo {pdf_path}...")
    doc = pymupdf.open(pdf_path)
    
    full_text = ""
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(img)
        full_text += text + "\n"
        
    lines = full_text.split('\n')
    
    current_campus = "Nao Informado"
    current_course = "Nao Informado"
    current_shift = "Não Informado"
    vagas_of = 0
    vagas_pr = 0
    
    students_data = []
    
    for line in lines:
        if line.startswith("Cidade:"):
            current_campus = line.replace("Cidade:", "").strip().title()
        elif line.startswith("Curso:"):
            c_name, c_campus, c_shift = parse_course_info(line, current_campus)
            current_course = c_name
            current_shift = c_shift
            if c_campus != "Nao Informado":
                current_campus = c_campus
        elif line.startswith("Vagas Ofertadas:"):
            vagas_of_str = line.replace("Vagas Ofertadas:", "").strip()
            nums = re.findall(r'\d+', vagas_of_str)
            vagas_of = sum(int(x) for x in nums)
        elif line.startswith("Vagas Preenchidas:"):
            match = re.search(r'\d+', line)
            if match: vagas_pr = int(match.group())
        else:
            match = re.search(r'(\d{5,})\s+([A-Z]+)\s+(\d{2,4}\.\d{1,4})', line)
            if match:
                quota = match.group(2)
                score = float(match.group(3))
                students_data.append({'quota': quota, 'score': score})
                
    if not students_data:
        print(f"Aviso: Nenhum aluno encontrado em {pdf_path}")
        return
        
    agg_data = {}
    for st in students_data:
        q = st['quota']
        sc = st['score']
        if q not in agg_data:
            agg_data[q] = {'spots': 0, 'scores': []}
        agg_data[q]['spots'] += 1
        agg_data[q]['scores'].append(sc)
        
    final_q_data = {}
    for q, data in agg_data.items():
        final_q_data[q] = {
            'spots': data['spots'],
            'min': min(data['scores']),
            'max': max(data['scores'])
        }
    
    leftover = vagas_of - vagas_pr if vagas_of > vagas_pr else 0
    
    c_upper = current_campus.upper()
    if 'BEL' in c_upper and 'M' in c_upper: current_campus = 'Belém'
    elif 'BRAGAN' in c_upper: current_campus = 'Bragança'
    elif 'CAMET' in c_upper: current_campus = 'Cametá'
    elif 'SALIN' in c_upper: current_campus = 'Salinópolis'
    elif 'TUCURU' in c_upper: current_campus = 'Tucuruí'
    elif 'MOCAJUBA' in c_upper: current_campus = 'Mocajuba'
    elif 'BAI' in c_upper: current_campus = 'Baião'
    elif 'MELGA' in c_upper: current_campus = 'Melgaço'
    elif 'M' in c_upper and 'DO RIO' in c_upper: current_campus = 'Mãe do Rio'
    elif 'CURU' in c_upper: current_campus = 'Curuçá'
    
    # Tratando erro do OCR para nomes de curso
    current_course = current_course.replace('**', '').strip()
    
    update_json("UFPA", 2026, current_course, current_campus, current_shift, final_q_data, leftover, vagas_pr)

def update_json(institution, year, course, campus, shift, quotas_data, leftover_spots, vagas_pr):
    pasta = os.path.join(
        PASTA_DESTINO,
        institution.upper(),
        str(year),
        normalizar_nome_arquivo(shift)
    )
    nome_arquivo = f"{normalizar_nome_arquivo(course)}_{normalizar_nome_arquivo(campus)}.json"
    caminho = os.path.join(pasta, nome_arquivo)
    
    if not os.path.exists(caminho):
        print(f"[ERRO] JSON nao encontrado: {caminho} para o curso OCR={course} campus={campus}")
        return
        
    with open(caminho, 'r', encoding='utf-8') as f:
        dados = json.load(f)
        
    oferta = dados["offerings"][0]
    total_spots = 0
    
    for quota_dict in oferta["competition_data"]:
        q_code = quota_dict["quota_code"]
        if q_code in quotas_data:
            spots = quotas_data[q_code].get("spots", 0)
            q_min = quotas_data[q_code].get("min", 0.0)
            q_max = quotas_data[q_code].get("max", 0.0)
            
            quota_dict["spots"] = spots
            quota_dict["previous_cutoff"] = q_min
            quota_dict["historical_max_score"] = q_max
            
            total_spots += spots
    
    oferta["total_spots_filled"] = total_spots
    oferta["leftover_spots"] = leftover_spots
    
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
        
    print(f"[OK] JSON atualizado: {caminho} (Total alunos: {total_spots})")

if __name__ == "__main__":
    brutos_dir = os.path.join(os.path.dirname(scripts_dir), "brutos", "ufpa", "newdatas")
    pdfs = glob.glob(os.path.join(brutos_dir, "**", "*.pdf"), recursive=True)
    
    print(f"Encontrados {len(pdfs)} PDFs para OCR.")
    for pdf in pdfs:
        try:
            process_pdf(pdf)
        except Exception as e:
            print(f"Erro ao processar {pdf}: {e}")
