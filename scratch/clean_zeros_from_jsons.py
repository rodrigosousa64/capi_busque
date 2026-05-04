import os
import json

base_path = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados"

def clean_jsons(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    modified = False
                    if "offerings" in data:
                        for offering in data["offerings"]:
                            if "competition_data" in offering:
                                original_len = len(offering["competition_data"])
                                # Only keep categories with more than 0 spots
                                offering["competition_data"] = [
                                    q for q in offering["competition_data"] 
                                    if q.get("spots", 0) > 0
                                ]
                                if len(offering["competition_data"]) != original_len:
                                    modified = True
                    
                    if modified:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, ensure_ascii=False, indent=4)
                        print(f"Cleaned: {file}")
                except Exception as e:
                    print(f"Error cleaning {file}: {e}")

if __name__ == "__main__":
    print("Starting JSON cleanup (removing zero-spot quotas)...")
    clean_jsons(base_path)
    print("Cleanup complete.")
