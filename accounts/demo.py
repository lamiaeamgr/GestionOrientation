"""Comptes de demonstration pre-remplis sur les ecrans de connexion."""

from types import SimpleNamespace

COMPTES_DEMO = {
    'candidat': SimpleNamespace(
        email='candidat@ensi.ma',
        password='CandidatENSI2026',
        first_name='Yasmine',
        last_name='Alaoui',
    ),
    'conseiller': SimpleNamespace(
        email='conseiller@ensi-uma.tn',
        password='ConseillerENSI2026',
        first_name='Sami',
        last_name='Ben Ali',
    ),
    'admin': SimpleNamespace(
        email='admin@ensi.ma',
        password='AdminENSI2026',
        first_name='Admin',
        last_name='ENSI',
    ),
}


def prefill_connexion(form, role):
    """Remplit email et mot de passe uniquement sur un GET (formulaire non soumis)."""
    compte = COMPTES_DEMO[role]
    if form.is_bound:
        return
    form.fields['username'].initial = compte.email
    form.fields['password'].widget.attrs['value'] = compte.password
