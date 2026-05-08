from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Comentario
from .forms import ComentarioForm

def lista_comentarios(request):
    comentarios = Comentario.objects.filter(ativo=True).order_by('-data_criacao')
    form = ComentarioForm()
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Você precisa estar logado para enviar um comentário.')
            return redirect('comentarios:lista')
            
        form = ComentarioForm(request.POST)
        if form.is_valid():
            novo_comentario = form.save(commit=False)
            novo_comentario.usuario = request.user
            novo_comentario.save()
            messages.success(request, 'Seu comentário foi enviado com sucesso! Obrigado pelo feedback.')
            return redirect('comentarios:lista')
            
    from datetime import date
    data_inicio = date(2026, 4, 28)
    dias_de_vida = (date.today() - data_inicio).days
            
    context = {
        'comentarios': comentarios,
        'form': form,
        'dias_de_vida': dias_de_vida
    }
    return render(request, 'comentarios/lista_comentarios.html', context)
