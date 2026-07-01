from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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

def adicionar_favorito_view(request, oferta_id):
    if request.method == 'POST':
        oferta = get_object_or_404(CourseOffering, id=oferta_id)
        favoritos = request.session.get('favoritos', [])
        if oferta_id not in favoritos:
            favoritos.append(oferta_id)
            request.session['favoritos'] = favoritos
            request.session.modified = True
        messages.success(request, f"Curso {oferta.course_name} adicionado aos favoritos!")
    
    # Tenta voltar para a página anterior (referer) ou para a busca
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('buscar_cursos')

def remover_favorito_view(request, oferta_id):
    if request.method == 'POST':
        oferta = get_object_or_404(CourseOffering, id=oferta_id)
        favoritos = request.session.get('favoritos', [])
        if oferta_id in favoritos:
            favoritos.remove(oferta_id)
            request.session['favoritos'] = favoritos
            request.session.modified = True
            messages.success(request, f"Curso {oferta.course_name} removido dos favoritos!")
            
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('buscar_cursos')

def listar_favoritos_view(request):
    if request.user.is_authenticated:
        try:
            perfil_db = request.user.perfil_candidato
            perfil_dataclass = PerfilCandidato(
                escola_publica=perfil_db.escola_publica,
                renda_sm=perfil_db.renda_sm,
                raca=perfil_db.raca,
                pcd=perfil_db.pcd
            )
        except PerfilCandidatoDB.DoesNotExist:
            messages.warning(request, "Você precisa configurar seu perfil antes de ver os favoritos.")
            return redirect('buscar_cursos')
    else:
        session_perfil = request.session.get('perfil_candidato', {
            'escola_publica': False,
            'renda_sm': 1.5,
            'raca': 'ND',
            'pcd': False
        })
        perfil_dataclass = PerfilCandidato(
            escola_publica=session_perfil['escola_publica'],
            renda_sm=session_perfil['renda_sm'],
            raca=session_perfil['raca'],
            pcd=session_perfil['pcd']
        )

    favoritos_ids = request.session.get('favoritos', [])
    ofertas_favoritas = CourseOffering.objects.filter(id__in=favoritos_ids)
    
    buscador = BuscadorDeNotas()
    avaliador = AvaliadorDeCotas(perfil_dataclass)
    
    resultados_favoritos = []
    
    for oferta in ofertas_favoritas:
        resultado = buscador.avaliar_oferta(oferta, perfil_dataclass, avaliador)
        if resultado:
            resultado['is_favorito'] = True # Para a view saber que já é favorito
            resultados_favoritos.append(resultado)

    return render(request, 'favoritos/lista.html', {
        'resultados': resultados_favoritos
    })
