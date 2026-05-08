import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cota_min_and_max_enem.models import CourseOffering

cursos = CourseOffering.objects.values_list('course_name', flat=True).distinct().order_by('course_name')
for c in cursos:
    print(c)
