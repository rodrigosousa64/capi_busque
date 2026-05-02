from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Favorito
from cota_min_and_max_enem.models import CourseOffering, PerfilCandidatoDB
import os
import sys

# Workaround para importar o módulo motor_cotas
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sub_dir = os.path.join(current_dir, 'cota_min_and_max_enem', 'motor_cotas')
if sub_dir not in sys.path:
    sys.path.append(sub_dir)

from buscador_notas import BuscadorDeNotas
from verificador_cotas import PerfilCandidato, AvaliadorDeCotas

@login_required
def adicionar_favorito_view(request, oferta_id):
    if request.method == 'POST':
        oferta = get_object_or_404(CourseOffering, id=oferta_id)
        Favorito.objects.get_or_create(user=request.user, oferta=oferta)
        messages.success(request, f"Curso {oferta.course_name} adicionado aos favoritos!")
    
    # Tenta voltar para a página anterior (referer) ou para a busca
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('buscar_cursos')

@login_required
def remover_favorito_view(request, oferta_id):
    if request.method == 'POST':
        oferta = get_object_or_404(CourseOffering, id=oferta_id)
        favorito = Favorito.objects.filter(user=request.user, oferta=oferta).first()
        if favorito:
            favorito.delete()
            messages.success(request, f"Curso {oferta.course_name} removido dos favoritos!")
            
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('buscar_cursos')

@login_required
def listar_favoritos_view(request):
    try:
        perfil_db = request.user.perfil_candidato
    except PerfilCandidatoDB.DoesNotExist:
        messages.warning(request, "Você precisa configurar seu perfil antes de ver os favoritos.")
        return redirect('buscar_cursos')

    perfil_dataclass = PerfilCandidato(
        escola_publica=perfil_db.escola_publica,
        renda_sm=perfil_db.renda_sm,
        raca=perfil_db.raca,
        pcd=perfil_db.pcd
    )

    favoritos = Favorito.objects.filter(user=request.user).select_related('oferta')
    
    buscador = BuscadorDeNotas()
    avaliador = AvaliadorDeCotas(perfil_dataclass)
    
    resultados_favoritos = []
    
    for fav in favoritos:
        resultado = buscador.avaliar_oferta(fav.oferta, perfil_dataclass, avaliador)
        if resultado:
            resultado['is_favorito'] = True # Para a view saber que já é favorito
            resultados_favoritos.append(resultado)

    return render(request, 'favoritos/lista.html', {
        'resultados': resultados_favoritos
    })
