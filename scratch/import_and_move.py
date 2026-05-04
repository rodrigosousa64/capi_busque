import os
import sys
import json
import shutil
import django

# Add project root to sys.path
sys.path.append(r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cota_min_and_max_enem.models import CourseOffering, QuotaData

source_dir = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados\novosdadosufpaqueforadobancodedados"
dest_base = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados"

def slugify(text):
    if not text: return "na"
    return text.strip().lower().replace(" ", "_")

count_files = 0
count_offerings = 0

for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.endswith('.json'):
            file_path = os.path.join(root, file)
            long_path = "\\\\?\\" + os.path.abspath(file_path) if os.name == 'nt' else file_path
            
            try:
                with open(long_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                institution = data.get("institution")
                year_reference = data.get("year_reference")
                
                if not institution or not year_reference:
                    print(f"Skipping {file}: missing metadata")
                    continue
                
                for off in data.get("offerings", []):
                    course = CourseOffering.objects.create(
                        institution=institution,
                        year_reference=year_reference,
                        course_name=off.get("course", ""),
                        campus=off.get("campus", ""),
                        degree=off.get("degree", ""),
                        shift=off.get("shift", ""),
                        total_spots_filled=off.get("total_spots_filled", 0),
                        leftover_spots=off.get("leftover_spots", 0)
                    )
                    
                    for q in off.get("competition_data", []):
                        QuotaData.objects.create(
                            course_offering=course,
                            quota_code=q.get("quota_code", ""),
                            description=q.get("description", ""),
                            spots=q.get("spots", 0),
                            previous_cutoff=q.get("previous_cutoff"),
                            historical_max_score=q.get("historical_max_score")
                        )
                    
                    count_offerings += 1
                    
                    shift_name = slugify(off.get("shift", "na"))
                    target_dir = os.path.join(dest_base, institution.upper(), str(year_reference), shift_name)
                    
                    if not os.path.exists(target_dir):
                        os.makedirs(target_dir, exist_ok=True)
                    
                    target_path = os.path.join(target_dir, file)
                    shutil.move(file_path, target_path)
                    print(f"Imported and moved: {file} -> {institution}/{year_reference}/{shift_name}/")
                
                count_files += 1
                
            except Exception as e:
                print(f"Error processing {file}: {e}")

print(f"Done! Processed {count_files} files and created {count_offerings} offerings in the database.")
