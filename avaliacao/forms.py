from django import forms
from .models import Avaliacao

class AvaliacaoForm(forms.ModelForm):
    avaliador = forms.CharField(required=True, label="Avaliador")
    loja = forms.CharField(required=True, label="Loja")

    class Meta:
        model = Avaliacao
        fields = [
            'avaliador', 'loja', 'pontualidade','organizacao', 'comunicacao',
            'resolucao_problemas', 'precisao', 'velocidade',
            'conhecimento_ferramentas', 'flexibilidade',
            'postura_profissional', 'priorizacao_tarefas', 'comentario'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'min': 1,
                'max': 5
            })
            # Define required como True apenas para campos que não são "comentario"
            self.fields[field].required = field != 'comentario'

