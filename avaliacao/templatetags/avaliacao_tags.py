# avaliacao/templatetags/avaliacao_tags.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Permite acessar um item de um dicionário usando uma variável no template.
    Uso: {{ meu_dicionario|get_item:minha_chave }}
    """
    if hasattr(dictionary, 'get'):
        return dictionary.get(key)
    return None