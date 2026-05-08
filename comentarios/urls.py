from django.urls import path
from . import views

app_name = 'comentarios'

urlpatterns = [
    path('', views.lista_comentarios, name='lista'),
]
