from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .demo import prefill_connexion
from .models import Utilisateur


def _style_auth(form):
    for field in form.fields.values():
        field.widget.attrs.setdefault('class', 'form-control')


class ConnexionCandidatForm(AuthenticationForm):
    """Connexion publique : candidats uniquement."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_auth(self)
        prefill_connexion(self, 'candidat')

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if user.est_admin:
            raise forms.ValidationError(
                "Les administrateurs doivent utiliser l'espace de connexion admin.",
                code='admin_login_required',
            )
        if user.est_conseiller:
            raise forms.ValidationError(
                "Les conseillers doivent utiliser l'espace de connexion conseiller.",
                code='conseiller_login_required',
            )


class ConnexionConseillerForm(AuthenticationForm):
    """Connexion reservee aux conseillers d'orientation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_auth(self)
        prefill_connexion(self, 'conseiller')

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.est_conseiller:
            raise forms.ValidationError(
                "Cet espace est reserve aux conseillers.",
                code='conseiller_only',
            )


class ConnexionAdminForm(AuthenticationForm):
    """Connexion reservee aux administrateurs."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style_auth(self)
        prefill_connexion(self, 'admin')

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.est_admin:
            raise forms.ValidationError(
                "Cet espace est reserve aux administrateurs.",
                code='admin_only',
            )


class InscriptionForm(UserCreationForm):
    """Inscription courte : prenom, nom, email, mot de passe."""

    first_name = forms.CharField(label='Prenom', max_length=150)
    last_name = forms.CharField(label='Nom', max_length=150)
    email = forms.EmailField(label='Adresse email')

    class Meta:
        model = Utilisateur
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = Utilisateur.Role.CANDIDAT
        if commit:
            user.save()
        return user
