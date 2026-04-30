from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroForm, PerfilForm, BuscaCursoForm
from .models import PerfilCandidatoDB
from django.utils import timezone
import os
import sys

# Workaround para importar o diretório com hifens
current_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(current_dir, 'Verificador-de-notas-de-cursos-max-e-min-das-universidades-federias-metropolinas-de-bel-m-')
if sub_dir not in sys.path:
    sys.path.append(sub_dir)

from buscador_notas import BuscadorDeNotas
from verificador_cotas import PerfilCandidato

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('buscar_cursos')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.last_login = timezone.now()
            user.save()
            # Criar perfil padrão automaticamente
            PerfilCandidatoDB.objects.create(user=user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, "Conta criada com sucesso! Por favor, atualize seu perfil.")
            return redirect('perfil')
    else:
        form = RegistroForm()
    return render(request, 'cota_min_and_max_enem/registro.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('buscar_cursos')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Bem-vindo, {username}!")
                return redirect('buscar_cursos')
            else:
                messages.error(request, "Usuário ou senha inválidos.")
        else:
            messages.error(request, "Usuário ou senha inválidos.")
    else:
        form = AuthenticationForm()
    return render(request, 'cota_min_and_max_enem/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "Você saiu com sucesso.")
    return redirect('login')

@login_required
def perfil_view(request):
    try:
        perfil_db = request.user.perfil_candidato
    except PerfilCandidatoDB.DoesNotExist:
        perfil_db = PerfilCandidatoDB.objects.create(user=request.user)

    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=perfil_db)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect('buscar_cursos')
    else:
        form = PerfilForm(instance=perfil_db)
        
    return render(request, 'cota_min_and_max_enem/perfil.html', {'form': form})

@login_required
def buscar_cursos_view(request):
    try:
        perfil_db = request.user.perfil_candidato
    except PerfilCandidatoDB.DoesNotExist:
        messages.warning(request, "Por favor, preencha seu perfil antes de buscar.")
        return redirect('perfil')

    form = BuscaCursoForm(request.GET or None)
    resultados = []

    if form.is_valid():
        curso_buscado = form.cleaned_data['curso']
        
        # Converter PerfilCandidatoDB para a dataclass PerfilCandidato
        perfil_dataclass = PerfilCandidato(
            escola_publica=perfil_db.escola_publica,
            renda_sm=perfil_db.renda_sm,
            raca=perfil_db.raca,
            pcd=perfil_db.pcd
        )
        
        buscador = BuscadorDeNotas()
        resultados = buscador.buscar_curso_para_perfil(curso_buscado, perfil_dataclass)

    return render(request, 'cota_min_and_max_enem/busca.html', {
        'form': form,
        'resultados': resultados
    })
