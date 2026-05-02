"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from cota_min_and_max_enem.models import CourseOffering

def home_view(request):
    cursos_aleatorios = list(CourseOffering.objects.order_by('?')[:4])
    
    for curso in cursos_aleatorios:
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

    return render(request, 'home/dashboard.html', {'cursos_aleatorios': cursos_aleatorios})

def regras_cotas_view(request):
    return render(request, 'home/regras_cotas.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('regras-cotas/', regras_cotas_view, name='regras_cotas'),
    path('cotas/', include('cota_min_and_max_enem.urls')),
    path('sobras/', include('vagas_sobrando.urls')),
]
