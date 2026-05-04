import os
import json

base_path = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados"

def count_quota_data(directory):
    total_files = 0
    total_offerings = 0
    total_quotas = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json') and "novosdados" not in root:
                total_files += 1
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if "offerings" in data:
                        for offering in data["offerings"]:
                            total_offerings += 1
                            if "competition_data" in offering:
                                total_quotas += len(offering["competition_data"])
                except: pass
                
    return total_files, total_offerings, total_quotas

if __name__ == "__main__":
    files, offerings, quotas = count_quota_data(base_path)
    print(f"Total JSON files: {files}")
    print(f"Total Offerings: {offerings}")
    print(f"Total QuotaData entries: {quotas}")
