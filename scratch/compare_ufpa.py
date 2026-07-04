import os
import sys
import django

sys.path.append(r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cota_min_and_max_enem.models import CourseOffering

ufpa_courses = CourseOffering.objects.filter(institution__iexact='UFPA')
db_courses = [(c.campus.upper(), c.course_name.upper()) for c in ufpa_courses]

with open(r"c:\Users\nawad\OneDrive\Desktop\MeusProjetos\capi_busque\scratch\db_courses.txt", "w", encoding="utf-8") as f:
    for campus, name in set(db_courses):
        f.write(f"{campus} | {name}\n")

print(f"Total unique campus+course combinations in DB: {len(set(db_courses))}")
