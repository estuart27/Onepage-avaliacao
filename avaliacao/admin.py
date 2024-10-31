# avaliacao/admin.py
from django.contrib import admin
from .models import Colaborador, Avaliacao

class AvaliacaoInline(admin.TabularInline):
    model = Avaliacao
    extra = 1  # Número de formulários em branco a serem exibidos

class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cargo','hub']
    search_fields = ['nome', 'cargo','hub']
    inlines = [AvaliacaoInline]

class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ['colaborador', 'pontualidade', 'organizacao', 'comunicacao', 'resolucao_problemas', 
                    'precisao', 'velocidade', 'conhecimento_ferramentas', 'flexibilidade', 
                    'postura_profissional', 'priorizacao_tarefas',]
    list_filter = ['colaborador']
    search_fields = ['colaborador__nome']

# Registrando os modelos no admin
admin.site.register(Colaborador, ColaboradorAdmin)
admin.site.register(Avaliacao, AvaliacaoAdmin)
