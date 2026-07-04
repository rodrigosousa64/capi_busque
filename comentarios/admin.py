from django.contrib import admin
from .models import Comentario

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ajudou_preparacao', 'data_criacao', 'ativo')
    list_filter = ('ativo', 'ajudou_preparacao', 'data_criacao')
    search_fields = ('usuario__username', 'usuario__email', 'texto_comentario')
    actions = ['aprovar_comentarios', 'ocultar_comentarios']

    def aprovar_comentarios(self, request, queryset):
        queryset.update(ativo=True)
    aprovar_comentarios.short_description = "Aprovar (Tornar Visível) comentários selecionados"

    def ocultar_comentarios(self, request, queryset):
        queryset.update(ativo=False)
    ocultar_comentarios.short_description = "Ocultar comentários selecionados"
