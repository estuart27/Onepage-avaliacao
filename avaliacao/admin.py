# avaliacao/admin.py

from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    Hub, 
    Colaborador, 
    Medalha, 
    AvaliacaoMensageiro, 
    AvaliacaoAssistente, 
    AvaliacaoRestaurante
)

# ---
# 1. Inlines para o ColaboradorAdmin
# ---
# (Permite ver e adicionar avaliações de dentro da página do colaborador)

class AvaliacaoMensageiroInline(admin.TabularInline):
    model = AvaliacaoMensageiro
    extra = 0  # Mostra 0 formulários em branco por padrão (mais limpo)
    readonly_fields = ('nota_comportamental', 'nota_operacional', 'nota_final')
    # fields = (...) # Você pode limitar os campos mostrados aqui

class AvaliacaoAssistenteInline(admin.TabularInline):
    model = AvaliacaoAssistente
    extra = 0
    readonly_fields = ('nota_comportamental', 'nota_operacional', 'nota_final')

class AvaliacaoRestauranteInline(admin.TabularInline):
    model = AvaliacaoRestaurante
    extra = 0
    readonly_fields = ('nota_final',)

# ---
# 2. Admin do Colaborador
# ---

@admin.register(Colaborador)
class ColaboradorAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cargo', 'hub')
    search_fields = ('nome', 'cargo', 'hub__nome') # Melhor para buscar pelo nome do hub
    list_filter = ('cargo', 'hub')
    inlines = [
        AvaliacaoMensageiroInline, 
        AvaliacaoAssistenteInline, 
        AvaliacaoRestauranteInline
    ]
    # (Os 3 inlines aparecerão. Caberá ao admin usar o correto para o cargo)

# ---
# 3. Admins das Avaliações (Gestor)
# ---

class AvaliacaoBaseAdmin(admin.ModelAdmin):
    """
    Admin BÁSICO ABSTRATO para compartilhar a lógica entre
    AvaliacaoMensageiroAdmin e AvaliacaoAssistenteAdmin.
    """
    list_display = ('colaborador', 'avaliador', 'data_avaliacao', 'nota_comportamental', 'nota_operacional', 'nota_final')
    list_filter = ('hub', 'data_avaliacao', 'avaliador')
    search_fields = ('colaborador__nome', 'avaliador__username')
    readonly_fields = ('nota_comportamental', 'nota_operacional', 'nota_final')
    
    # Organiza os campos comuns em seções
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('avaliador', 'hub', 'colaborador', 'data_avaliacao')
        }),
        ('🧠 Avaliação Comportamental', {
            'classes': ('collapse',), # Começa fechado para economizar espaço
            'fields': ('proatividade', 'responsabilidade', 'trabalho_em_equipe', 
                       'comunicacao', 'resiliencia', 'postura_profissional', 
                       'evolucao_individual', 'comentario_comportamental')
        }),
    )

@admin.register(AvaliacaoMensageiro)
class AvaliacaoMensageiroAdmin(AvaliacaoBaseAdmin):
    # Herda os fieldsets do BaseAdmin e adiciona o seu
    fieldsets = AvaliacaoBaseAdmin.fieldsets + (
        ('🧩 Avaliação Operacional (Mensageiro)', {
            'fields': ('trm5', 'erros_pedido', 'cumprimento_metas', 'pontualidade',
                       'organizacao_praca', 'comunicacao_central', 'comentario_operacional')
        }),
    )

@admin.register(AvaliacaoAssistente)
class AvaliacaoAssistenteAdmin(AvaliacaoBaseAdmin):
    # Herda os fieldsets do BaseAdmin e adiciona o seu
    fieldsets = AvaliacaoBaseAdmin.fieldsets + (
        ('🧩 Avaliação Operacional (Assistente)', {
            'fields': ('controle_fila_nba5', 'eficiencia_distribuicao', 'monitoramento_ativo',
                       'cumprimento_processos', 'resolucao_imprevistos', 'comentario_operacional')
        }),
    )

# ---
# 4. Admin da Avaliação (Restaurante)
# ---

@admin.register(AvaliacaoRestaurante)
class AvaliacaoRestauranteAdmin(admin.ModelAdmin):
    list_display = ('colaborador', 'nome_restaurante', 'nota_final', 'data_avaliacao')
    list_filter = ('hub', 'data_avaliacao', 'nome_restaurante')
    search_fields = ('colaborador__nome', 'nome_restaurante')
    readonly_fields = ('nota_final',)
    
    # Organiza os campos em seções
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome_restaurante', 'nome_avaliador_restaurante', 'hub', 'colaborador', 'data_avaliacao')
        }),
        ('Critérios de Avaliação', {
            'fields': ('rapidez_atendimento', 'eficiencia_resolucao', 'clareza_comunicacao',
                       'profissionalismo', 'suporte_gestao_pedidos', 'proatividade',
                       'disponibilidade', 'satisfacao_geral', 'comentario')
        }),
    )

# ---
# 5. Admin de Medalha (Seu código original, que está ótimo)
# ---

@admin.register(Medalha)
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

# ---
# 6. Registro Simples (para o Hub)
# ---

admin.site.register(Hub)

# NOTA: Os outros modelos já foram registrados usando o decorador @admin.register()
# Os modelos antigos 'Avaliacao' e 'Avaliacao_Restaurante' não são mais registrados.