from django.urls import path
from . import views

urlpatterns = [
    path('', views.sobras_view, name='vagas_sobrando_lista'),
]
