import re

from django import forms

from .catalogues import (
    VILLES_MAROC,
    etablissements_pour,
    matieres_pour,
    specialites_pour,
    types_pour,
)
from .models import CentreInteret, InteretCandidat, Matiere, NoteAcademique, ProfilAcademique, ProfilCandidat


def _slug(nom):
    return re.sub(r'[^a-z0-9]+', '_', nom.lower()).strip('_')


class ProfilCandidatForm(forms.ModelForm):
    class Meta:
        model = ProfilCandidat
        fields = ('objectif', 'niveau_entree', 'ville', 'date_naissance')
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'ville': forms.TextInput(attrs={'list': 'villes-maroc', 'placeholder': 'Ex. : Tanger'}),
            'objectif': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['niveau_entree'].required = True
        self.fields['objectif'].required = True
        self.fields['objectif'].label = 'Votre projet (avant toute recommandation)'
        self.fields['date_naissance'].input_formats = ['%Y-%m-%d']
        self.villes = VILLES_MAROC


class ProfilAcademiqueForm(forms.ModelForm):
    """Formulaire dynamique : filiere marocaine puis specialite FSJES / FST / BTS."""

    class Meta:
        model = ProfilAcademique
        fields = (
            'type_diplome', 'specialite', 'etablissement', 'ville_etablissement',
            'annee_obtention', 'moyenne_generale',
            'moyenne_annee_1', 'moyenne_annee_2', 'moyenne_annee_3',
        )

    def __init__(self, *args, niveau=None, type_diplome=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.niveau = niveau
        type_diplome = type_diplome or self.initial.get('type_diplome') or self.instance.type_diplome

        self.fields['type_diplome'] = forms.ChoiceField(
            label='Filiere / type de diplome',
            choices=[('', '---------')] + list(types_pour(niveau)),
            required=True,
            help_text='Liste officielle des filieres marocaines selon votre niveau.',
        )
        specialites = specialites_pour(niveau, type_diplome)
        if specialites:
            self.fields['specialite'] = forms.ChoiceField(
                label='Specialite / modules',
                choices=[('', '---------')] + list(specialites),
                required=True,
                help_text='Les matieres proposees s\'adaptent a cette specialite.',
            )
        else:
            self.fields.pop('specialite', None)

        self.fields['etablissement'].widget = forms.TextInput(
            attrs={'list': 'etablissements-suggeres', 'placeholder': 'Nom de l\'etablissement'}
        )
        self.etablissements = etablissements_pour(type_diplome)
        self.fields['ville_etablissement'].widget = forms.TextInput(
            attrs={'list': 'villes-maroc', 'placeholder': 'Ville de l\'etablissement'}
        )

        if niveau == ProfilCandidat.NiveauEntree.BAC:
            self.fields.pop('moyenne_annee_1', None)
            self.fields.pop('moyenne_annee_2', None)
            self.fields.pop('moyenne_annee_3', None)
            self.fields['type_diplome'].label = 'Filiere du Baccalaureat'
            self.fields['moyenne_generale'].label = 'Moyenne generale du Bac (/20)'
            self.fields['moyenne_generale'].help_text = 'Note figurant sur le releve du Bac.'
        elif niveau == ProfilCandidat.NiveauEntree.BAC2:
            self.fields.pop('moyenne_annee_3', None)
            self.fields['type_diplome'].label = 'Type d\'etablissement (FSJES, FST, BTS...)'
            self.fields['moyenne_annee_1'].label = 'Moyenne 1ere annee (/20)'
            self.fields['moyenne_annee_2'].label = 'Moyenne 2e annee (/20)'
            self.fields['moyenne_generale'].label = 'Moyenne generale (/20)'
        elif niveau == ProfilCandidat.NiveauEntree.BAC3:
            self.fields['type_diplome'].label = 'Type de licence / bachelor'
            self.fields['moyenne_annee_1'].label = 'Moyenne 1ere annee (/20)'
            self.fields['moyenne_annee_2'].label = 'Moyenne 2e annee (/20)'
            self.fields['moyenne_annee_3'].label = 'Moyenne 3e annee (/20)'
            self.fields['moyenne_generale'].label = 'Moyenne generale (/20)'


class NotesFiliereForm(forms.Form):
    """Notes pre-remplies selon la filiere (plus de liste unique style Bac)."""

    def __init__(self, *args, academique=None, niveau='', type_diplome='', specialite='', **kwargs):
        super().__init__(*args, **kwargs)
        self.academique = academique
        self.noms = matieres_pour(niveau, type_diplome, specialite)
        existantes = {}
        if academique:
            existantes = {
                n.matiere.nom: n.note
                for n in academique.notes.select_related('matiere')
            }
        for nom in self.noms:
            self.fields[f'note_{_slug(nom)}'] = forms.DecimalField(
                label=nom,
                min_value=0,
                max_value=20,
                decimal_places=2,
                required=False,
                initial=existantes.get(nom),
                widget=forms.NumberInput(attrs={
                    'min': 0, 'max': 20, 'step': '0.01',
                    'placeholder': '/20',
                }),
            )

    def save(self):
        if not self.academique:
            return
        slugs = {f'note_{_slug(nom)}': nom for nom in self.noms}
        for champ, nom in slugs.items():
            valeur = self.cleaned_data.get(champ)
            matiere, _ = Matiere.objects.get_or_create(nom=nom)
            if valeur is None:
                NoteAcademique.objects.filter(
                    academique=self.academique, matiere=matiere
                ).delete()
            else:
                NoteAcademique.objects.update_or_create(
                    academique=self.academique,
                    matiere=matiere,
                    defaults={'note': valeur},
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
