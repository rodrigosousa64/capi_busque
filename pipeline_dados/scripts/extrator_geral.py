import os
import glob
import re
import sys
import traceback
import pdfplumber

# Adiciona scripts ao path para poder importar
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from extrair_pdf import (
    gerar_template_json, 
    salvar_template, 
    PASTA_BRUTOS, 
    PASTA_DESTINO,
    normalizar_nome_arquivo
)

def criar_json_e_salvar(institution, year, course, campus, degree, shift, quotas_data, leftover_spots=0):
    """
    Recebe os metadados do curso e um dicionario quotas_data no formato:
    {
        'AC': {'spots': 10, 'min': 600.0, 'max': 750.0},
        ...
    }
    Gera o template e preenche com os valores reais.
    """
    try:
        # Gera o esqueleto
        template = gerar_template_json(institution, year, course, campus, degree, shift)
        
        # Preenche os dados
        oferta = template["offerings"][0]
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
        
        # Salva o arquivo. A funcao salvar_template ja verifica se existe para evitar reescrita (duplicados)
        salvar_template(template, institution, year, shift, course, campus)
    except Exception as e:
        print(f"[ERRO] Erro ao salvar {institution} {course}: {e}")
        traceback.print_exc()

def processar_ufra():
    print("Processando UFRA...")
    pasta_ufra = os.path.join(PASTA_BRUTOS, "ufra")
    pdfs = glob.glob(os.path.join(pasta_ufra, "*.pdf"))
    
    for pdf_path in pdfs:
        try:
            print(f"Lendo {pdf_path}...")
            with pdfplumber.open(pdf_path) as pdf:
                current_campus = "Não Informado"
                current_course = "Não Informado"
                current_degree = "Bacharelado"
                current_shift = "Não Informado"
                
                courses_data = {}
                
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text: continue
                    lines = text.split('\n')
                    for line in lines:
                        if line.startswith("Campus:"):
                            current_campus = line.replace("Campus:", "").strip()
                        elif line.startswith("Curso:"):
                            full_course = line.replace("Curso:", "").strip()
                            if "(" in full_course:
                                parts = full_course.split("(")
                                current_course = parts[0].strip()
                                current_degree = parts[1].replace(")", "").strip()
                            else:
                                current_course = full_course
                                current_degree = "Bacharelado" # default se não achar
                                
                            key = (current_campus, current_course, current_degree, current_shift)
                            if key not in courses_data:
                                courses_data[key] = []
                        elif re.match(r'^\d+\s+\d+', line):
                            # Ex: "1 76484 LÍVIA RIBEIRO DOS SANTOS 753,38 AC AC"
                            parts = line.split()
                            if len(parts) >= 6:
                                mod_ocupada = parts[-1]
                                nota_str = parts[-3]
                                try:
                                    score = float(nota_str.replace(',', '.'))
                                    key = (current_campus, current_course, current_degree, current_shift)
                                    courses_data[key].append({'quota': mod_ocupada, 'score': score})
                                except:
                                    pass
                                    
                # Agora agrega os dados
                for key, students in courses_data.items():
                    campus, course, degree, shift = key
                    agg_data = {}
                    for st in students:
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
                    
                    criar_json_e_salvar("UFRA", 2026, course, campus, degree, shift, final_q_data)
        except Exception as e:
            print(f"Erro em {pdf_path}: {e}")
            traceback.print_exc()

def processar_ufpa():
    print("Processando UFPA...")
    pasta_ufpa = os.path.join(PASTA_BRUTOS, "ufpa")
    pdfs = glob.glob(os.path.join(pasta_ufpa, "*.pdf"))
    
    for pdf_path in pdfs:
        try:
            print(f"Lendo {pdf_path}...")
            with pdfplumber.open(pdf_path) as pdf:
                current_campus = "Não Informado"
                current_course = "Não Informado"
                current_degree = "Bacharelado"
                current_shift = "Não Informado"
                vagas_of = 0
                vagas_pr = 0
                
                students_data = []
                
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text: continue
                    lines = text.split('\n')
                    for line in lines:
                        if line.startswith("Cidade:"):
                            current_campus = line.replace("Cidade:", "").strip()
                        elif line.startswith("Curso:"):
                            # Ex: ADMINISTRACAO (BAC/EXT/MATUTINO/ENTRADA 1)
                            full_course = line.replace("Curso:", "").strip()
                            if "(" in full_course:
                                parts = full_course.split("(")
                                current_course = parts[0].strip()
                                details = parts[1].replace(")", "").split("/")
                                if len(details) >= 3:
                                    current_degree = details[0].strip()
                                    current_shift = details[2].strip()
                            else:
                                current_course = full_course
                        elif line.startswith("Vagas Ofertadas:"):
                            vagas_of_str = line.replace("Vagas Ofertadas:", "").strip()
                            nums = re.findall(r'\d+', vagas_of_str)
                            vagas_of = sum(int(x) for x in nums)
                        elif line.startswith("Vagas Preenchidas:"):
                            match = re.search(r'\d+', line)
                            if match: vagas_pr = int(match.group())
                        else:
                            # Tenta bater com o aluno: INSCRIÇÃO COTA NOTA COLOCAÇÃO
                            # Ex: "ANDERSON ... 151332 ERPCD 531.12 1ª (ERPCD) ✔️"
                            match = re.search(r'(\d{5,})\s+([A-Z]+)\s+(\d{2,4}\.\d{1,4})\s+(\d+ª)', line)
                            if match:
                                quota = match.group(2)
                                score = float(match.group(3))
                                students_data.append({'quota': quota, 'score': score})
                
                if students_data:
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
                    
                    criar_json_e_salvar("UFPA", 2026, current_course, current_campus, current_degree, current_shift, final_q_data, leftover)
        except Exception as e:
            print(f"Erro em {pdf_path}: {e}")
            traceback.print_exc()

def processar_uepa():
    print("Processando UEPA...")
    pasta_uepa = os.path.join(PASTA_BRUTOS, "uepa")
    pdfs = glob.glob(os.path.join(pasta_uepa, "*.pdf"))
    
    for pdf_path in pdfs:
        try:
            print(f"Lendo {pdf_path}...")
            with pdfplumber.open(pdf_path) as pdf:
                courses_data = {}
                current_course_key = None
                
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text: continue
                    lines = text.split('\n')
                    for line in lines:
                        # CABECALHO: "ALTAMIRA / ENFERMAGEM (Bacharelado / Integral / Não Modular / 1° Semestre)"
                        match_course = re.match(r'^([^/]+)\s*/\s*([^\(]+)\s*\(([^/]+)\s*/\s*([^/]+)\s*/', line)
                        if match_course:
                            campus = match_course.group(1).strip()
                            course = match_course.group(2).strip()
                            degree = match_course.group(3).strip()
                            shift = match_course.group(4).strip()
                            current_course_key = (campus, course, degree, shift)
                            if current_course_key not in courses_data:
                                courses_data[current_course_key] = {
                                    'max_min': {},
                                    'spots': {}
                                }
                        
                        elif line.startswith("MÁXIMAS:") and current_course_key:
                            parts = line.replace("MÁXIMAS:", "").strip().split()
                            for i in range(0, len(parts)-1, 2):
                                q = parts[i].replace(':', '')
                                try:
                                    val = float(parts[i+1])
                                    if q not in courses_data[current_course_key]['max_min']:
                                        courses_data[current_course_key]['max_min'][q] = {}
                                    courses_data[current_course_key]['max_min'][q]['max'] = val
                                except: pass

                        elif line.startswith("MÍNIMAS:") and current_course_key:
                            parts = line.replace("MÍNIMAS:", "").strip().split()
                            for i in range(0, len(parts)-1, 2):
                                q = parts[i].replace(':', '')
                                try:
                                    val = float(parts[i+1])
                                    if q not in courses_data[current_course_key]['max_min']:
                                        courses_data[current_course_key]['max_min'][q] = {}
                                    courses_data[current_course_key]['max_min'][q]['min'] = val
                                except: pass
                                
                        else:
                            # Tenta ler vaga: Ex "2025008000 7 G 710.38 1º"
                            match_student = re.match(r'^(\d{10,})\s+\d+\s+([A-Z])\s+(\d+\.\d+)\s+', line)
                            if match_student and current_course_key:
                                quota = match_student.group(2)
                                if quota not in courses_data[current_course_key]['spots']:
                                    courses_data[current_course_key]['spots'][quota] = 0
                                courses_data[current_course_key]['spots'][quota] += 1
                                
                # Salva cada curso encontrado na UEPA
                for key, data in courses_data.items():
                    campus, course, degree, shift = key
                    final_q_data = {}
                    
                    # Combina max_min e spots
                    all_quotas = set(data['max_min'].keys()) | set(data['spots'].keys())
                    for q in all_quotas:
                        spots = data['spots'].get(q, 0)
                        q_min = data['max_min'].get(q, {}).get('min', 0.0)
                        q_max = data['max_min'].get(q, {}).get('max', 0.0)
                        
                        # as vezes a cota não teve ingressantes, ignorar.
                        if spots > 0 or q_min > 0 or q_max > 0:
                            final_q_data[q] = {
                                'spots': spots,
                                'min': q_min,
                                'max': q_max
                            }
                            
                    if final_q_data:
                        criar_json_e_salvar("UEPA", 2026, course, campus, degree, shift, final_q_data)
        except Exception as e:
            print(f"Erro em {pdf_path}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    print("Iniciando Extração de Dados...")
    processar_ufra()
    processar_ufpa()
    processar_uepa()
    print("Extração finalizada com sucesso!")
