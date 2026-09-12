from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Utilisateur


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
