from django import forms
from .models import Avaliacao

class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = [
            'pontualidade', 'organizacao', 'comunicacao',
            'resolucao_problemas', 'precisao', 'velocidade',
            'conhecimento_ferramentas', 'flexibilidade',
            'postura_profissional', 'priorizacao_tarefas','comentario'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'min': 1,
                'max': 5,
                'required': True
            })