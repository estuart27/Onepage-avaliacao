from django import template

register = template.Library()

@register.filter
def repeat(value, times):
    """Repete uma string 'times' vezes."""
    return value * int(times)
