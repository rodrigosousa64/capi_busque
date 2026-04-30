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

# Workaround para importar o módulo motor_cotas
current_dir = os.path.dirname(os.path.abspath(__file__))
sub_dir = os.path.join(current_dir, 'motor_cotas')
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
            messages.success(request, "Conta criada com sucesso!")
            return redirect('buscar_cursos')
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
def buscar_cursos_view(request):
    try:
        perfil_db = request.user.perfil_candidato
    except PerfilCandidatoDB.DoesNotExist:
        perfil_db = PerfilCandidatoDB.objects.create(user=request.user)

    # Lógica de atualização de perfil (POST)
    if request.method == 'POST':
        perfil_form = PerfilForm(request.POST, instance=perfil_db)
        if perfil_form.is_valid():
            perfil_form.save()
            messages.success(request, "Perfil atualizado com sucesso!")
            return redirect(request.get_full_path()) # Redireciona mantendo a query de busca se houver
    else:
        perfil_form = PerfilForm(instance=perfil_db)

    # Lógica de busca (GET)
    busca_form = BuscaCursoForm(request.GET or None)
    resultados = []

    if busca_form.is_valid():
        curso_buscado = busca_form.cleaned_data['curso']
        
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
        'busca_form': busca_form,
        'perfil_form': perfil_form,
        'resultados': resultados
    })
