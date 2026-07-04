import os
import re
import json
import pdfplumber
import traceback
import sys

# Adiciona caminhos para importar os scripts existentes
scripts_dir = os.path.dirname(os.path.abspath(__file__))
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from extrair_pdf import gerar_template_json, normalizar_nome_arquivo

# Configurações de caminhos
RAIZ_PIPELINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_IFPA = os.path.join(RAIZ_PIPELINE, "brutos", "ifpa", "IFPA 2026 _ TODOS OS CAMPOS.pdf")
PASTA_DESTINO = os.path.join(RAIZ_PIPELINE, "dados_processados", "novosdadosufpaqueforadobancodedados")

# Mapeamento de Cotas IFPA (Baseado em padrões PSU e JSONs existentes)
MAPA_COTAS = {
    "AC": "AC",
    "RI_PPI": "L1",
    "RI_EP": "L2",
    "IR_PPI": "L3",
    "RS_PPI": "L3",
    "IR_EP": "L4",
    "RS_EP": "L4",
    "RI_PPI_PCD": "L5",
    "RI_EP_PCD": "L6",
    "IR_PPI_PCD": "L7",
    "RS_PPI_PCD": "L7",
    "IR_EP_PCD": "L8",
    "RS_EP_PCD": "L8",
    # Mapeamento para códigos AXX (Sisu/MEC novos)
    "A11": "L1", "A13": "L2", "A19": "L3", "A06": "L5", "A04": "L7"
}

def salvar_json_ifpa(dados, course, campus, shift):
    nome_arquivo = f"ifpa_{normalizar_nome_arquivo(course)}_{normalizar_nome_arquivo(campus)}_{normalizar_nome_arquivo(shift)}_2026.json"
    caminho = os.path.join(PASTA_DESTINO, nome_arquivo)
    
    with open(caminho, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)
    print(f"[OK] IFPA JSON: {nome_arquivo}")

def extrair_ifpa():
    print(f"Iniciando extração do IFPA: {os.path.basename(PDF_IFPA)}")
    if not os.path.exists(PASTA_DESTINO):
        os.makedirs(PASTA_DESTINO)

    # Dicionário para armazenar os dados agregados por curso
    # Chave: (campus, course, degree, shift)
    courses_db = {}

    current_campus = "Não Informado"
    current_course = "Não Informado"
    current_degree = "Bacharelado"
    current_shift = "Não Informado"

    try:
        with pdfplumber.open(PDF_IFPA) as pdf:
            for page_idx, page in enumerate(pdf.pages):
                text = page.extract_text()
                if not text: continue
                lines = text.split('\n')
                
                for line in lines:
                    # Tenta identificar cabeçalho de curso
                    # Ex: "Graduao - Geografia - Campus Abaetetuba Licenciatura - Turno: Vespertino"
                    if "Gradua" in line and "Campus" in line:
                        # Limpeza básica do texto distorcido pelo PDF
                        clean_line = line.replace("", "a").replace("", "o").replace("", "u").replace("", "e")
                        
                        match_header = re.search(r'Graduacao\s*-\s*([^-]+)-\s*Campus\s*([^\s-]+)\s*([^\-]+)-\s*Turno:\s*(\w+)', clean_line)
                        if match_header:
                            current_course = match_header.group(1).strip()
                            current_campus = match_header.group(2).strip()
                            current_degree = match_header.group(3).strip()
                            current_shift = match_header.group(4).strip()
                            
                            key = (current_campus, current_course, current_degree, current_shift)
                            if key not in courses_db:
                                courses_db[key] = []
                    
                    # Tenta identificar linha de aluno APROVADO
                    # Ex: "605564 ... 3515,10 703,02 RI_PPI 1 Aprovado(a) AC"
                    if "Aprovado(a)" in line:
                        parts = line.split()
                        if len(parts) >= 6:
                            # A cota de inscrição geralmente está perto do status ou no fim
                            # Vamos procurar pelo código de cota mapeado
                            quota_code = "AC"
                            score = 0.0
                            
                            # Tenta achar a nota (formato XXXX,XX ou XXX,XX)
                            for p in parts:
                                if "," in p and re.match(r'^\d+,\d+$', p):
                                    val = float(p.replace(',', '.'))
                                    if val > 100: # Evita pegar a média (703,02) e pega o total (3515,10) se for o caso
                                        # Na verdade o sistema usa a Média (ex: 703,02)
                                        if val < 1000: score = val
                            
                            # Tenta achar a cota
                            for p in parts:
                                if p in MAPA_COTAS:
                                    quota_code = MAPA_COTAS[p]
                                    break
                            
                            if score > 0:
                                key = (current_campus, current_course, current_degree, current_shift)
                                if key in courses_db:
                                    courses_db[key].append({'quota': quota_code, 'score': score})

            # Após ler tudo, gerar os JSONs
            for key, students in courses_db.items():
                campus, course, degree, shift = key
                if not students: continue
                
                # Agrupar por cota
                agg_data = {}
                for st in students:
                    q = st['quota']
                    sc = st['score']
                    if q not in agg_data:
                        agg_data[q] = {'spots': 0, 'scores': []}
                    agg_data[q]['spots'] += 1
                    agg_data[q]['scores'].append(sc)
                
                # Gerar template
                template = gerar_template_json("IFPA", 2026, course, campus, degree, shift)
                oferta = template["offerings"][0]
                total_spots = 0
                
                for quota_dict in oferta["competition_data"]:
                    q_code = quota_dict["quota_code"]
                    if q_code in agg_data:
                        spots = agg_data[q_code]['spots']
                        q_min = min(agg_data[q_code]['scores'])
                        q_max = max(agg_data[q_code]['scores'])
                        
                        quota_dict["spots"] = spots
                        quota_dict["previous_cutoff"] = q_min
                        quota_dict["historical_max_score"] = q_max
                        total_spots += spots
                
                oferta["total_spots_filled"] = total_spots
                # Salvar
                salvar_json_ifpa(template, course, campus, shift)

    except Exception as e:
        print(f"[ERRO] Falha geral: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    extrair_ifpa()
    print("\nExtração IFPA finalizada!")
