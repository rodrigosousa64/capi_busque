import os
import glob
import json

def clean_jsons():
    # Caminho base para os JSONs da UFPA de 2026 gerados
    base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "dados_processados", "UFPA", "2026")
    
    jsons = glob.glob(os.path.join(base_dir, "**", "*.json"), recursive=True)
    count_cleaned = 0
    
    for j_path in jsons:
        try:
            with open(j_path, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                
            ofertas = dados.get("offerings", [])
            modified = False
            
            for oferta in ofertas:
                original_competition = oferta.get("competition_data", [])
                new_competition = []
                
                for quota in original_competition:
                    spots = quota.get("spots", 0)
                    q_min = quota.get("previous_cutoff", 0.0)
                    q_max = quota.get("historical_max_score", 0.0)
                    
                    # Regra do usuario: if spots > 0 or q_min > 0 or q_max > 0:
                    if spots > 0 or q_min > 0 or q_max > 0:
                        new_competition.append(quota)
                    else:
                        modified = True
                        
                if modified:
                    oferta["competition_data"] = new_competition
                    
            if modified:
                with open(j_path, 'w', encoding='utf-8') as f:
                    json.dump(dados, f, ensure_ascii=False, indent=4)
                count_cleaned += 1
                
        except Exception as e:
            print(f"Erro ao processar {j_path}: {e}")
            
    print(f"Limpeza concluida. {count_cleaned} arquivos JSON foram ajustados para remover cotas vazias.")

if __name__ == "__main__":
    clean_jsons()
