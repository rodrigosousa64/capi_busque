import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from cota_min_and_max_enem.models import CourseOffering

courses = CourseOffering.objects.values('institution', 'course_name', 'campus').distinct().order_by('institution', 'course_name', 'campus')

for c in courses:
    print(f"{c['course_name']} - {c['institution']} ({c['campus']})")
