from django import forms
from django.forms import inlineformset_factory

from .models import (
    CentreInteret,
    InteretCandidat,
    Matiere,
    NoteAcademique,
    ProfilAcademique,
    ProfilCandidat,
)


class ProfilCandidatForm(forms.ModelForm):
    class Meta:
        model = ProfilCandidat
        fields = ('niveau_entree', 'ville', 'date_naissance')
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['niveau_entree'].required = True
        self.fields['date_naissance'].input_formats = ['%Y-%m-%d']


class ProfilAcademiqueForm(forms.ModelForm):
    """Formulaire dynamique : les champs affiches dependent du niveau d'entree."""

    class Meta:
        model = ProfilAcademique
        fields = (
            'type_diplome', 'specialite', 'etablissement', 'ville_etablissement',
            'annee_obtention', 'moyenne_generale',
            'moyenne_annee_1', 'moyenne_annee_2', 'moyenne_annee_3',
            'modules_principaux',
        )
        widgets = {
            'modules_principaux': forms.Textarea(attrs={'rows': 3}),
        }

    CHOIX_TYPES = {
        ProfilCandidat.NiveauEntree.BAC: ProfilAcademique.TypeDiplomeBac.choices,
        ProfilCandidat.NiveauEntree.BAC2: ProfilAcademique.TypeDiplomeBac2.choices,
        ProfilCandidat.NiveauEntree.BAC3: ProfilAcademique.TypeDiplomeBac3.choices,
    }

    def __init__(self, *args, niveau=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.niveau = niveau
        self.fields['type_diplome'] = forms.ChoiceField(
            label='Type / serie du diplome',
            choices=[('', '---------')] + list(self.CHOIX_TYPES.get(niveau, [])),
        )
        # Champs masques selon le niveau d'entree
        if niveau == ProfilCandidat.NiveauEntree.BAC:
            del self.fields['moyenne_annee_1']
            del self.fields['moyenne_annee_2']
            del self.fields['moyenne_annee_3']
            del self.fields['modules_principaux']
            self.fields['type_diplome'].label = 'Type / serie du Baccalaureat'
            self.fields['moyenne_generale'].label = 'Note generale du Bac (/20)'
        elif niveau == ProfilCandidat.NiveauEntree.BAC2:
            del self.fields['moyenne_annee_3']
            self.fields['moyenne_annee_1'].label = 'Moyenne 1ere annee (/20)'
            self.fields['moyenne_annee_2'].label = 'Moyenne 2e annee (/20)'
            self.fields['moyenne_generale'].label = 'Moyenne generale (/20)'
        elif niveau == ProfilCandidat.NiveauEntree.BAC3:
            self.fields['moyenne_annee_1'].label = 'Moyenne 1ere annee (/20)'
            self.fields['moyenne_annee_2'].label = 'Moyenne 2e annee (/20)'
            self.fields['moyenne_annee_3'].label = 'Moyenne 3e annee (/20)'
            self.fields['moyenne_generale'].label = 'Moyenne generale (/20)'


NoteAcademiqueFormSet = inlineformset_factory(
    ProfilAcademique,
    NoteAcademique,
    fields=('matiere', 'note'),
    extra=3,
    can_delete=True,
    widgets={'note': forms.NumberInput(attrs={'min': 0, 'max': 20, 'step': '0.01'})},
)


class InteretsForm(forms.Form):
    """Selection des centres d'interet et preferences d'activite."""

    domaines = forms.ModelMultipleChoiceField(
        queryset=CentreInteret.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Domaines d'interet",
    )
    activites = forms.ModelMultipleChoiceField(
        queryset=CentreInteret.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Preferences d'activite",
    )

    def __init__(self, *args, profil=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.profil = profil
        self.fields['domaines'].queryset = CentreInteret.objects.filter(
            categorie=CentreInteret.Categorie.DOMAINE
        )
        self.fields['activites'].queryset = CentreInteret.objects.filter(
            categorie=CentreInteret.Categorie.ACTIVITE
        )
        if profil:
            selectionnes = profil.interets.values_list('interet_id', flat=True)
            self.fields['domaines'].initial = self.fields['domaines'].queryset.filter(
                pk__in=selectionnes
            )
            self.fields['activites'].initial = self.fields['activites'].queryset.filter(
                pk__in=selectionnes
            )

    def save(self):
        if not self.profil:
            return
        InteretCandidat.objects.filter(profil=self.profil).delete()
        for interet in list(self.cleaned_data['domaines']) + list(self.cleaned_data['activites']):
            InteretCandidat.objects.create(profil=self.profil, interet=interet)
