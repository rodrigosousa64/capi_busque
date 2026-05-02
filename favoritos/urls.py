from django.urls import path
from . import views

urlpatterns = [
    path('', views.listar_favoritos_view, name='listar_favoritos'),
    path('adicionar/<int:oferta_id>/', views.adicionar_favorito_view, name='adicionar_favorito'),
    path('remover/<int:oferta_id>/', views.remover_favorito_view, name='remover_favorito'),
]
