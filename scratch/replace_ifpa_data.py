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

source_dir = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados\novosdadosufpaqueforadobancodedados\IFPA_DEFINITIVO"
dest_base = r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\pipeline_dados\dados_processados\IFPA"

def slugify(text):
    if not text: return "na"
    return str(text).strip().lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u").replace("ç", "c")

# 1. CLEANUP DATABASE (Only IFPA)
print("Cleaning up old IFPA data from database...")
CourseOffering.objects.filter(institution="IFPA").delete()

# 2. CLEANUP FILESYSTEM (IFPA folder)
print("Cleaning up old IFPA files from pipeline...")
if os.path.exists(dest_base):
    shutil.rmtree(dest_base)
os.makedirs(dest_base, exist_ok=True)

# 3. IMPORT AND MOVE
print("Importing new IFPA 2026 data...")
count = 0
for file in os.listdir(source_dir):
    if file.endswith('.json'):
        path = os.path.join(source_dir, file)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            inst = data.get("institution")
            year = data.get("year_reference")
            
            for off in data.get("offerings", []):
                # Save to DB
                course = CourseOffering.objects.create(
                    institution=inst,
                    year_reference=year,
                    course_name=off.get("course"),
                    campus=off.get("campus"),
                    degree=off.get("degree"),
                    shift=off.get("shift"),
                    total_spots_filled=off.get("total_spots_filled", 0),
                    leftover_spots=off.get("leftover_spots", 0)
                )
                for q in off.get("competition_data", []):
                    QuotaData.objects.create(
                        course_offering=course,
                        quota_code=q.get("quota_code"),
                        description=q.get("description"),
                        spots=q.get("spots", 0),
                        previous_cutoff=q.get("previous_cutoff"),
                        historical_max_score=q.get("historical_max_score")
                    )
                
                # Move File
                shift_dir = slugify(off.get("shift", "na"))
                final_dir = os.path.join(dest_base, str(year), shift_dir)
                os.makedirs(final_dir, exist_ok=True)
                
                shutil.copy(path, os.path.join(final_dir, file))
                count += 1
        except Exception as e:
            print(f"Error with {file}: {e}")

print(f"Successfully replaced IFPA data. {count} offerings created and files organized.")
