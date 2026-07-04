import os
import json
from collections import defaultdict

base_path = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados"

def generate_report(directory):
    # Stats: stats[institution][shift] = count
    stats = defaultdict(lambda: defaultdict(int))
    total_by_inst = defaultdict(int)
    total_by_shift = defaultdict(int)
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json') and "novosdados" not in root:
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    inst = data.get("institution", "UNKNOWN").upper()
                    if "offerings" in data:
                        for offering in data["offerings"]:
                            shift = offering.get("shift", "N/A").upper()
                            stats[inst][shift] += 1
                            total_by_inst[inst] += 1
                            total_by_shift[shift] += 1
                except: pass
                
    return stats, total_by_inst, total_by_shift

if __name__ == "__main__":
    stats, by_inst, by_shift = generate_report(base_path)
    
    print("# Análise Estatística de Cursos")
    print("\n## Por Universidade e Turno")
    for inst, shifts in sorted(stats.items()):
        print(f"\n### {inst} (Total: {by_inst[inst]})")
        for shift, count in sorted(shifts.items()):
            print(f"- {shift}: {count}")
            
    print("\n## Resumo por Turno (Geral)")
    for shift, count in sorted(by_shift.items()):
        print(f"- {shift}: {count}")
