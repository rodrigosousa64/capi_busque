from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('oque_eu_sei_sobre_voce', views.oque_eu_sei_sobre_voce, name='oque_eu_sei_sobre_voce'),
]