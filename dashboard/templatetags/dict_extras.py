from django import template
from django.templatetags.static import static

register = template.Library()


@register.filter
def get_item(dictionnaire, cle):
    """Accede a un element de dictionnaire dans un template."""
    if dictionnaire is None:
        return None
    return dictionnaire.get(cle)


def _cover_path(formation):
    texte = f'{getattr(formation, "nom", "")} {getattr(formation, "domaine", "")}'.lower()
    if any(mot in texte for mot in ('big data', 'intelligence', 'ia', 'data')):
        return 'img/bigdata-ia.jpg'
    if any(mot in texte for mot in ('web', 'mobile', 'informatique', 'logiciel')):
        return 'img/genie-informatique.jpg'
    if any(mot in texte for mot in ('industriel', 'qualit', 'production')):
        return 'img/genie-industriel.jpg'
    if 'civil' in texte:
        return 'img/genie-civil.png'
    if any(mot in texte for mot in ('prepa', 'preparatoire')):
        return 'img/cycle-prepa.jpg'
    if any(mot in texte for mot in ('finance', 'marketing', 'logistique', 'management', 'gestion')):
        return 'img/management.jpg'
    return 'img/hero-campus.jpg'


@register.simple_tag
def formation_cover(formation):
    """Image de la formation : upload admin, sinon visuel ENSI par defaut."""
    image = getattr(formation, 'image', None)
    if image:
        try:
            if image.url:
                return image.url
        except ValueError:
            pass
    return static(_cover_path(formation))
