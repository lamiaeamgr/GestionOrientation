"""Isolation des sessions par espace de travail.

Un meme navigateur peut garder trois connexions ouvertes :
admin, conseiller et candidat (espace public). Chaque espace
utilise un cookie de session distinct.
"""
from importlib import import_module

from django.conf import settings

ADMIN = 'admin'
CONSEILLER = 'conseiller'
PUBLIC = 'public'

COOKIE_NAMES = {
    ADMIN: 'sessionid_admin',
    CONSEILLER: 'sessionid_conseiller',
    PUBLIC: 'sessionid_public',
}

AUTH_USER_ID = '_auth_user_id'


def workspace_pour_chemin(path):
    chemin = path or '/'
    if (
        chemin.startswith('/administration/')
        or chemin.startswith('/comptes/connexion-admin')
        or chemin.startswith('/comptes/deconnexion-admin')
    ):
        return ADMIN
    if (
        chemin.startswith('/espace-conseiller/')
        or chemin.startswith('/comptes/connexion-conseiller')
        or chemin.startswith('/comptes/deconnexion-conseiller')
    ):
        return CONSEILLER
    return PUBLIC


def nom_cookie(workspace):
    return COOKIE_NAMES.get(workspace, COOKIE_NAMES[PUBLIC])


def utilisateur_depuis_cookie(request, workspace):
    """Charge l'utilisateur authentifie d'un autre espace, sans le melanger."""
    from accounts.models import Utilisateur

    session_key = request.COOKIES.get(nom_cookie(workspace))
    if not session_key:
        return None
    moteur = import_module(settings.SESSION_ENGINE)
    session = moteur.SessionStore(session_key)
    user_id = session.get(AUTH_USER_ID)
    if not user_id:
        return None
    try:
        return Utilisateur.objects.get(pk=user_id, is_active=True)
    except Utilisateur.DoesNotExist:
        return None


def personnel_interne(request):
    """True si un admin ou un conseiller est connecte dans ce navigateur."""
    admin = utilisateur_depuis_cookie(request, ADMIN)
    if admin is not None and admin.est_admin:
        return True
    conseiller = utilisateur_depuis_cookie(request, CONSEILLER)
    return conseiller is not None and conseiller.est_conseiller
