# avaliacao/forms.py

from django import forms
from .models import (
    AvaliacaoMensageiro, 
    AvaliacaoAssistente, 
    AvaliacaoRestaurante
)

# ---
# 1. Formulário de Avaliação do GESTOR para o MENSAGEIRO
# ---

class AvaliacaoMensageiroForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoMensageiro
        
        # Lista de campos que o gestor irá preencher
        fields = [
            # --- 🧠 CAMPOS COMPORTAMENTAIS (da Base) ---
            'proatividade',
            'responsabilidade',
            'trabalho_em_equipe',
            'comunicacao',
            'resiliencia',
            'postura_profissional',
            'evolucao_individual',
            
            # --- 🧩 CAMPOS OPERACIONAIS (Específicos do Mensageiro) ---
            'trm5',
            'erros_pedido',
            'cumprimento_metas',
            'pontualidade',
            'organizacao_praca',
            'comunicacao_central',
            
            # --- Comentários ---
            'comentario_comportamental',
            'comentario_operacional'
        ]
        
        # BÔNUS: Isso transforma os campos de nota (1-5) em botões de rádio
        # Fica muito melhor para o usuário do que um dropdown.
        widgets = {
            'proatividade': forms.RadioSelect,
            'responsabilidade': forms.RadioSelect,
            'trabalho_em_equipe': forms.RadioSelect,
            'comunicacao': forms.RadioSelect,
            'resiliencia': forms.RadioSelect,
            'postura_profissional': forms.RadioSelect,
            'evolucao_individual': forms.RadioSelect,
            
            'trm5': forms.RadioSelect,
            'erros_pedido': forms.RadioSelect,
            'cumprimento_metas': forms.RadioSelect,
            'pontualidade': forms.RadioSelect,
            'organizacao_praca': forms.RadioSelect,
            'comunicacao_central': forms.RadioSelect,
            
            'comentario_comportamental': forms.Textarea(attrs={'rows': 3}),
            'comentario_operacional': forms.Textarea(attrs={'rows': 3}),
        }

# ---
# 2. Formulário de Avaliação do GESTOR para o ASSISTENTE
# ---

class AvaliacaoAssistenteForm(forms.ModelForm):
    class Meta:
        model = AvaliacaoAssistente
        
        fields = [
            # --- 🧠 CAMPOS COMPORTAMENTAIS (da Base) ---
            'proatividade',
            'responsabilidade',
            'trabalho_em_equipe',
            'comunicacao',
            'resiliencia',
            'postura_profissional',
            'evolucao_individual',
            
            # --- 🧩 CAMPOS OPERACIONAIS (Específicos do Assistente) ---
            'controle_fila_nba5',
            'eficiencia_distribuicao',
            'monitoramento_ativo',
            'cumprimento_processos',
            'resolucao_imprevistos',
            
            # --- Comentários ---
            'comentario_comportamental',
            'comentario_operacional'
        ]
        
        # BÔNUS: Mesma melhoria de UI com RadioSelect
        widgets = {
            'proatividade': forms.RadioSelect,
            'responsabilidade': forms.RadioSelect,
            'trabalho_em_equipe': forms.RadioSelect,
            'comunicacao': forms.RadioSelect,
            'resiliencia': forms.RadioSelect,
            'postura_profissional': forms.RadioSelect,
            'evolucao_individual': forms.RadioSelect,

            'controle_fila_nba5': forms.RadioSelect,
            'eficiencia_distribuicao': forms.RadioSelect,
            'monitoramento_ativo': forms.RadioSelect,
            'cumprimento_processos': forms.RadioSelect,
            'resolucao_imprevistos': forms.RadioSelect,

            'comentario_comportamental': forms.Textarea(attrs={'rows': 3}),
            'comentario_operacional': forms.Textarea(attrs={'rows': 3}),
        }

# ---
# 3. Formulário de Avaliação do RESTAURANTE para o COLABORADOR
# ---

class AvaliacaoRestauranteForm(forms.ModelForm):
    # (Este era o seu 'AvaliacaoMensageiroForm' antigo, agora com nome correto)
    class Meta:
        model = AvaliacaoRestaurante
        
        # Campos que o restaurante irá preencher
        fields = [
            'nome_restaurante',
            'nome_avaliador_restaurante',
            'rapidez_atendimento',
            'eficiencia_resolucao',
            'clareza_comunicacao',
            'profissionalismo',
            'suporte_gestao_pedidos',
            'proatividade',
            'disponibilidade',
            'satisfacao_geral',
            'comentario'
        ]
        
        # Rótulos amigáveis para os campos de texto
        labels = {
            'nome_restaurante': 'Nome do seu Restaurante',
            'nome_avaliador_restaurante': 'Seu Nome (Opcional)',
        }
        
        # BÔNUS: Mesma melhoria de UI com RadioSelect
        widgets = {
            'rapidez_atendimento': forms.RadioSelect,
            'eficiencia_resolucao': forms.RadioSelect,
            'clareza_comunicacao': forms.RadioSelect,
            'profissionalismo': forms.RadioSelect,
            'suporte_gestao_pedidos': forms.RadioSelect,
            'proatividade': forms.RadioSelect,
            'disponibilidade': forms.RadioSelect,
            'satisfacao_geral': forms.RadioSelect,
            'comentario': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove o 'required' do nome do avaliador, como no seu model
        self.fields['nome_avaliador_restaurante'].required = False