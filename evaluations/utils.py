"""Pseudonymisation des emails des evaluateurs.

L'adresse email n'est jamais stockee en clair : on calcule une empreinte
deterministe (HMAC-SHA256 avec une cle serveur) qui sert a verifier
l'eligibilite et l'unicite de la reponse, sans permettre la
re-identification directe.
"""
import hashlib
import hmac

from django.conf import settings


def normaliser_email(email):
    """Normalise l'adresse : minuscules, sans espaces superflus."""
    return (email or '').strip().lower()


def empreinte_email(email):
    """Retourne l'identifiant pseudonyme irreversible de l'email."""
    cle = getattr(settings, 'EVALUATION_HMAC_KEY', settings.SECRET_KEY)
    return hmac.new(
        cle.encode('utf-8'),
        normaliser_email(email).encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()


DOMAINES_ENSI = ('ensi.ma', 'ensit.ma', 'ensi-uma.tn')


def email_est_ensi(email):
    domaine = normaliser_email(email).rsplit('@', 1)[-1]
    return domaine in DOMAINES_ENSI


def email_est_personnel(email):
    """Un admin ou un conseiller ne peut jamais evaluer un enseignant."""
    from accounts.models import Utilisateur

    utilisateur = Utilisateur.objects.filter(
        email__iexact=normaliser_email(email)
    ).first()
    if utilisateur is None:
        return False
    return utilisateur.est_admin or utilisateur.est_conseiller
