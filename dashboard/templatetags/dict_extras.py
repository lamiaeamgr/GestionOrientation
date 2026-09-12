from django import template

register = template.Library()


@register.filter
def get_item(dictionnaire, cle):
    """Accede a un element de dictionnaire dans un template."""
    if dictionnaire is None:
        return None
    return dictionnaire.get(cle)
