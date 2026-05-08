from django.db import models
from django.contrib.auth.models import User

class Comentario(models.Model):
    AJUDOU_CHOICES = [
        ('S', 'Sim'),
        ('P', 'Parcialmente'),
        ('N', 'Ainda não'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentarios')
    texto_comentario = models.TextField(verbose_name='Seu comentário sobre o Capi Busque')
    ajudou_preparacao = models.CharField(
        max_length=1, 
        choices=AJUDOU_CHOICES, 
        verbose_name='O site te ajudou na preparação/decisão para o ENEM?',
        default='S'
    )
    data_criacao = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True, verbose_name='Ativo (Visível para o público)')

    def __str__(self):
        return f'Comentário de {self.usuario.username} em {self.data_criacao.strftime("%d/%m/%Y")}'

    class Meta:
        verbose_name = 'Comentário'
        verbose_name_plural = 'Comentários'
        ordering = ['-data_criacao']
