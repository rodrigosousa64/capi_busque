from django.shortcuts import render
from cota_min_and_max_enem.models import CourseOffering

def sobras_view(request):
    cursos_com_sobra = CourseOffering.objects.filter(leftover_spots__gt=0).order_by('-leftover_spots')
    
    for curso in cursos_com_sobra:
        quotas = curso.quotas.all()
        curso.min_quota = None
        curso.max_quota = None
        
        if quotas.exists():
            valid_min = [q for q in quotas if q.previous_cutoff is not None and q.previous_cutoff > 0]
            valid_max = [q for q in quotas if q.historical_max_score is not None and q.historical_max_score > 0]
            
            if valid_min:
                curso.min_quota = min(valid_min, key=lambda q: q.previous_cutoff)
            if valid_max:
                curso.max_quota = max(valid_max, key=lambda q: q.historical_max_score)

    return render(request, 'vagas_sobrando/sobras.html', {'cursos_com_sobra': cursos_com_sobra})
