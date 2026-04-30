from django import forms
from django.contrib.auth.models import User
from .models import PerfilCandidatoDB

class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Senha")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirme a Senha")

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': 'Nome de Usuário',
            'email': 'E-mail'
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "As senhas não coincidem.")
        return cleaned_data


class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilCandidatoDB
        fields = ['escola_publica', 'renda_sm', 'raca', 'pcd']


class BuscaCursoForm(forms.Form):
    curso = forms.CharField(
        max_length=200, 
        label="Qual curso você deseja buscar?",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ex: Engenharia da Computação, Medicina...',
            'class': 'form-control'
        })
    )
