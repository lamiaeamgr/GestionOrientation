from django import forms
from django.utils import timezone

from .models import DisponibiliteConseiller, RendezVous


class DisponibiliteForm(forms.ModelForm):
    class Meta:
        model = DisponibiliteConseiller
        fields = ('date_heure_debut', 'date_heure_fin')
        widgets = {
            'date_heure_debut': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
            'date_heure_fin': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for champ in ('date_heure_debut', 'date_heure_fin'):
            self.fields[champ].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned = super().clean()
        debut = cleaned.get('date_heure_debut')
        fin = cleaned.get('date_heure_fin')
        if debut and fin:
            if fin <= debut:
                raise forms.ValidationError(
                    'La fin du creneau doit etre posterieure au debut.'
                )
            if debut < timezone.now():
                raise forms.ValidationError(
                    'Le creneau ne peut pas etre dans le passe.'
                )
        return cleaned


class ReservationForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ('motif',)
        widgets = {
            'motif': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Objet du rendez-vous (questions, hesitation entre filieres...)',
            }),
        }


class NoteConseillerForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ('note_conseiller', 'statut')
        widgets = {
            'note_conseiller': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Compte-rendu et recommandation apres entretien...',
            }),
        }
