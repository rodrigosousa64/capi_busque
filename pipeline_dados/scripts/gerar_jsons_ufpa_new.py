import os
import re
import sys

scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from extrair_pdf import gerar_template_json, salvar_template

RAIZ_PROJETO = os.path.dirname(os.path.dirname(scripts_dir))
FALTA_TXT_PATH = os.path.join(RAIZ_PROJETO, "faltacursosufpa.txt")

def parse_txt_and_generate_jsons():
    print(f"Lendo {FALTA_TXT_PATH}...")
    
    with open(FALTA_TXT_PATH, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        
    current_campus = "Nao Informado"
    count = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        match = re.match(r'^\d+\s*-\s*(.+?)\s*\((.+?)\)', line)
        if match:
            course_name_raw = match.group(1).strip()
            details_raw = match.group(2).strip()
            
            parts = details_raw.split('/')
            degree_map = {
                'LIC': 'Licenciatura',
                'BAC': 'Bacharelado',
                'TECNO': 'Tecnologo',
                'ABI': 'Área Básica de Ingresso',
                'LIC ': 'Licenciatura'
            }
            
            degree_code = parts[0].strip()
            if 'ABI' in course_name_raw:
                degree = 'Área Básica de Ingresso'
            else:
                degree = degree_map.get(degree_code, 'Bacharelado')
            
            shift = "Não Informado"
            for p in parts:
                p_clean = p.strip().upper()
                if p_clean in ['MATUTINO', 'VESPERTINO', 'NOTURNO', 'INTEGRAL']:
                    shift = p_clean.capitalize()
                    break
                    
            oferta_match = re.search(r'-\s*\(OFERTA EM (.+?)\)', line)
            if oferta_match:
                course_campus = oferta_match.group(1).strip().title()
            else:
                course_campus = current_campus
                
            course_name_clean = course_name_raw.replace('**', '').strip()
            
            c_upper = course_campus.upper()
            if 'BEL' in c_upper and 'M' in c_upper: course_campus = 'Belém'
            elif 'BRAGAN' in c_upper: course_campus = 'Bragança'
            elif 'CAMET' in c_upper: course_campus = 'Cametá'
            elif 'SALIN' in c_upper: course_campus = 'Salinópolis'
            elif 'TUCURU' in c_upper: course_campus = 'Tucuruí'
            elif 'MAC' in c_upper and 'P' in c_upper: course_campus = 'Macapá'
            elif 'MOCAJUBA' in c_upper: course_campus = 'Mocajuba'
            elif 'BAI' in c_upper: course_campus = 'Baião'
            elif 'MELGA' in c_upper: course_campus = 'Melgaço'
            elif 'M' in c_upper and 'DO RIO' in c_upper: course_campus = 'Mãe do Rio'
            elif 'CURU' in c_upper: course_campus = 'Curuçá'
            
            print(f"Gerando: {course_name_clean} | {degree} | {shift} | {course_campus}")
            
            dados = gerar_template_json(
                institution="UFPA",
                year=2026,
                course=course_name_clean,
                campus=course_campus,
                degree=degree,
                shift=shift
            )
            salvar_template(dados, "UFPA", 2026, shift, course_name_clean, course_campus)
            count += 1
        else:
            # É o campus
            current_campus = line.strip().title()
            c_upper = current_campus.upper()
            if 'BEL' in c_upper and 'M' in c_upper: current_campus = 'Belém'
            elif 'BRAGAN' in c_upper: current_campus = 'Bragança'
            elif 'CAMET' in c_upper: current_campus = 'Cametá'
            elif 'SALIN' in c_upper: current_campus = 'Salinópolis'
            elif 'TUCURU' in c_upper: current_campus = 'Tucuruí'

    print(f"Total de templates gerados: {count}")

if __name__ == "__main__":
    parse_txt_and_generate_jsons()
