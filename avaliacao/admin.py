# avaliacao/admin.py
from django.contrib import admin
from .models import Colaborador, Avaliacao,Hub,Medalha,Avaliacao_Restaurante

class AvaliacaoInline(admin.TabularInline):
    model = Avaliacao
    extra = 1  # Número de formulários em branco a serem exibidos

class AvaliacaoRestauranteInline(admin.TabularInline):
    model = Avaliacao_Restaurante
    extra = 1  # Número de formulários em branco a serem exibidos

class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo', 'hub']
    search_fields = ['nome', 'cargo', 'hub']
    inlines = [AvaliacaoInline, AvaliacaoRestauranteInline] 


class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['avaliador', 'loja', 'media_geral', 'ver_comentario']
    list_filter = ['avaliador']
    search_fields = ['avaliador']
    
    def media_geral(self, obj):
        campos_avaliacao = [
            obj.organizacao, obj.comunicacao, obj.resolucao_problemas,
            obj.precisao, obj.velocidade, obj.conhecimento_ferramentas,
            obj.flexibilidade, obj.postura_profissional, obj.priorizacao_tarefas
        ]
        media = sum(filter(None, campos_avaliacao)) / len([nota for nota in campos_avaliacao if nota is not None])
        return round(media, 2)

    media_geral.short_description = 'Média Geral'
    
    def ver_comentario(self, obj):
        return obj.comentario if obj.comentario else "Sem comentário"
    
    ver_comentario.short_description = 'Comentário'

    # Especifica quais campos adicionais mostrar na visualização detalhada
    fields = ('avaliador', 'loja', 'organizacao', 'comunicacao', 'resolucao_problemas', 
              'precisao', 'velocidade', 'conhecimento_ferramentas', 'flexibilidade', 
              'postura_profissional', 'priorizacao_tarefas', 'comentario')
              

from django.utils.safestring import mark_safe

class MedalhaAdmin(admin.ModelAdmin):
    list_display = ("colaborador", "tipo", "preview_medalha")
    list_filter = ("tipo",)
    search_fields = ("colaborador__nome", "tipo")

    def preview_medalha(self, obj):
        """Exibe a imagem da medalha no Django Admin"""
        if obj.tipo:
            return mark_safe(f'<img src="{obj.get_medalha_url()}" width="50" height="50" style="border-radius:8px;"/>')
        return "Sem imagem"

    preview_medalha.short_description = "Prévia"

admin.site.register(Medalha, MedalhaAdmin)




admin.site.register(Hub)
admin.site.register(Colaborador, ColaboradorAdmin)
admin.site.register(Avaliacao, AvaliacaoAdmin)
admin.site.register(Avaliacao_Restaurante)


