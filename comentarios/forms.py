from django import forms
from .models import Comentario

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto_comentario', 'ajudou_preparacao']
        widgets = {
            'texto_comentario': forms.Textarea(attrs={
                'class': 'form-control custom-textarea',
                'placeholder': 'Deixe seu depoimento sobre como o site te ajudou...',
                'rows': 4
            }),
            'ajudou_preparacao': forms.Select(attrs={
                'class': 'form-control custom-select'
            }),
        }
