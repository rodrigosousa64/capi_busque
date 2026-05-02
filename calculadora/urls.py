from django.urls import path
from . import views

urlpatterns = [
    path('', views.calculadora_view, name='calculadora_index'),
]
