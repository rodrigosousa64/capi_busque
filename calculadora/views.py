from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from favoritos.models import Favorito
from cota_min_and_max_enem.models import PerfilCandidatoDB
import os
import sys

# Workaround para importar o módulo motor_cotas
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sub_dir = os.path.join(current_dir, 'cota_min_and_max_enem', 'motor_cotas')
if sub_dir not in sys.path:
    sys.path.append(sub_dir)

from buscador_notas import BuscadorDeNotas
from verificador_cotas import PerfilCandidato, AvaliadorDeCotas

# login_required removido
def calculadora_view(request):
    resultados_favoritos = []
    
    if request.user.is_authenticated:
        try:
            perfil_db = request.user.perfil_candidato
        except PerfilCandidatoDB.DoesNotExist:
            perfil_db = PerfilCandidatoDB.objects.create(user=request.user)

        perfil_dataclass = PerfilCandidato(
            escola_publica=perfil_db.escola_publica,
            renda_sm=perfil_db.renda_sm,
            raca=perfil_db.raca,
            pcd=perfil_db.pcd
        )

        favoritos = Favorito.objects.filter(user=request.user).select_related('oferta')
        
        buscador = BuscadorDeNotas()
        avaliador = AvaliadorDeCotas(perfil_dataclass)
        
        for fav in favoritos:
            resultado = buscador.avaliar_oferta(fav.oferta, perfil_dataclass, avaliador)
            if resultado:
                resultado['is_favorito'] = True
                resultados_favoritos.append(resultado)

    return render(request, 'calculadora/index.html', {
        'resultados': resultados_favoritos
    })
