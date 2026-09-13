from django import forms
from django.contrib.auth.password_validation import validate_password
from django.db.models import Q

from accounts.models import Utilisateur
from candidats.models import CentreInteret, ProfilCandidat
from conseil.models import ProfilConseiller
from evaluations.models import (
    CampagneEvaluation,
    Enseignant,
    EtudiantInterne,
    GroupeEtudiant,
    Module,
    QuestionEvaluation,
)
from evaluations.utils import email_est_ensi, email_est_personnel, normaliser_email
from formations.models import Formation, PrerequisFormation
from orientation.models import OptionReponse, PonderationOptionFormation, Question, Questionnaire


def styliser(form):
    for field in form.fields.values():
        widget = field.widget
        if isinstance(widget, (forms.SelectMultiple, forms.CheckboxSelectMultiple)):
            widget.attrs.setdefault('class', 'form-select')
            if isinstance(widget, forms.SelectMultiple):
                widget.attrs.setdefault('size', '8')
        elif isinstance(widget, forms.Select):
            widget.attrs.setdefault('class', 'form-select')
        elif isinstance(widget, forms.CheckboxInput):
            widget.attrs.setdefault('class', 'form-check-input')
        elif isinstance(widget, forms.Textarea):
            widget.attrs.setdefault('class', 'form-control')
            widget.attrs.setdefault('rows', widget.attrs.get('rows', 3))
        elif not isinstance(widget, forms.HiddenInput):
            widget.attrs.setdefault('class', 'form-control')
    return form


class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = (
            'nom', 'domaine', 'niveau', 'parcours', 'parent',
            'description', 'conditions_admission', 'competences_recherchees',
            'matieres_importantes', 'debouches', 'reconnaissance', 'est_active',
            'image',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)
        self.fields['parent'].queryset = Formation.objects.order_by('nom')
        if self.instance.pk:
            self.fields['parent'].queryset = self.fields['parent'].queryset.exclude(
                pk=self.instance.pk
            )
        self.fields['parent'].required = False


class PrerequisForm(forms.ModelForm):
    class Meta:
        model = PrerequisFormation
        fields = ('matiere', 'note_minimale', 'poids')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)


class EnseignantForm(forms.ModelForm):
    class Meta:
        model = Enseignant
        fields = ('prenom', 'nom')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)


class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ('code', 'nom')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)


class GroupeForm(forms.ModelForm):
    class Meta:
        model = GroupeEtudiant
        fields = ('nom', 'filiere', 'annee_universitaire')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)


class CampagneForm(forms.ModelForm):
    class Meta:
        model = CampagneEvaluation
        fields = (
            'titre', 'enseignant', 'module', 'groupe', 'semestre',
            'statut', 'date_debut', 'date_fin',
        )
        widgets = {
            'date_debut': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
            'date_fin': forms.DateTimeInput(
                attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for champ in ('date_debut', 'date_fin'):
            self.fields[champ].input_formats = ['%Y-%m-%dT%H:%M']
            self.fields[champ].required = False
        self.fields['suggere_ia'] = forms.BooleanField(
            label='Proposer des questions et reponses avec l IA',
            required=False,
            initial=not self.instance.pk,
            help_text='A partir du titre : criteres notes + commentaires.',
        )
        styliser(self)


class QuestionEvaluationForm(forms.ModelForm):
    class Meta:
        model = QuestionEvaluation
        fields = ('texte', 'type_question', 'ordre')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)


class AffectationClasseForm(forms.Form):
    groupes = forms.ModelMultipleChoiceField(
        label='Classes / groupes',
        queryset=GroupeEtudiant.objects.none(),
        required=False,
        widget=forms.SelectMultiple(),
        help_text='Tous les etudiants ENSI de ces classes sont autorises (empreinte HMAC).',
    )
    filiere = forms.ChoiceField(
        label='Ou toute une filiere',
        required=False,
        help_text='Selectionne tous les etudiants internes de cette filiere.',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groupes'].queryset = GroupeEtudiant.objects.order_by(
            'filiere', 'nom'
        )
        filieres = (
            EtudiantInterne.objects.exclude(filiere='')
            .values_list('filiere', flat=True)
            .distinct()
            .order_by('filiere')
        )
        self.fields['filiere'].choices = [('', '---------')] + [
            (nom, nom) for nom in filieres
        ]
        styliser(self)

    def etudiants(self):
        groupes = self.cleaned_data.get('groupes')
        filiere = self.cleaned_data.get('filiere')
        filtres = Q()
        if groupes:
            filtres |= Q(groupe__in=groupes)
        if filiere:
            filtres |= Q(filiere=filiere)
        if not filtres:
            return []
        return list(EtudiantInterne.objects.filter(filtres))

    def emails_normalises(self):
        uniques, ignores = [], []
        vus = set()
        for etudiant in self.etudiants():
            email = normaliser_email(etudiant.email)
            if email in vus:
                continue
            vus.add(email)
            if email_est_personnel(email) or not email_est_ensi(email):
                ignores.append(email)
                continue
            uniques.append(email)
        return uniques, ignores


class EtudiantInterneForm(forms.ModelForm):
    class Meta:
        model = EtudiantInterne
        fields = ('prenom', 'nom', 'email', 'filiere', 'groupe')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)

    def clean_email(self):
        email = normaliser_email(self.cleaned_data['email'])
        if not email_est_ensi(email):
            raise forms.ValidationError(
                "L'adresse doit etre un email ENSI (ensi.ma, ensit.ma)."
            )
        if email_est_personnel(email):
            raise forms.ValidationError('Un compte admin ou conseiller ne peut pas evaluer.')
        return email


class InteretForm(forms.ModelForm):
    class Meta:
        model = CentreInteret
        fields = ('nom', 'categorie')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)


class QuestionnaireForm(forms.ModelForm):
    suggere_ia = forms.BooleanField(
        label='Proposer des questions et reponses avec l IA',
        required=False,
        initial=True,
        help_text='Genere un questionnaire de mise en situation a partir du titre.',
    )

    class Meta:
        model = Questionnaire
        fields = ('titre', 'version', 'est_actif')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)


class QuestionOrientationForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ('texte', 'type_question', 'ordre')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)


class OptionReponseForm(forms.ModelForm):
    class Meta:
        model = OptionReponse
        fields = ('texte',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)


class PonderationForm(forms.ModelForm):
    class Meta:
        model = PonderationOptionFormation
        fields = ('formation', 'poids')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        styliser(self)
        self.fields['formation'].queryset = Formation.objects.filter(
            est_active=True
        ).order_by('nom')


class ConseillerForm(forms.Form):
    first_name = forms.CharField(label='Prenom', max_length=150)
    last_name = forms.CharField(label='Nom', max_length=150)
    email = forms.EmailField(label='Adresse email')
    password = forms.CharField(
        label='Mot de passe',
        required=False,
        widget=forms.PasswordInput,
        help_text='Laisser vide pour conserver le mot de passe actuel.',
    )
    specialite = forms.CharField(
        label="Domaine d'accompagnement", max_length=150, required=False
    )
    biographie = forms.CharField(
        label='Biographie', required=False, widget=forms.Textarea
    )

    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance = instance
        if instance is not None:
            user = instance.utilisateur
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
            self.fields['specialite'].initial = instance.specialite
            self.fields['biographie'].initial = instance.biographie
        else:
            self.fields['password'].required = True
            self.fields['password'].help_text = ''
        styliser(self)

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = Utilisateur.objects.filter(email__iexact=email)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.utilisateur_id)
        if qs.exists():
            raise forms.ValidationError('Cette adresse email est deja utilisee.')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            validate_password(password)
        return password

    def save(self):
        data = self.cleaned_data
        if self.instance is None:
            user = Utilisateur.objects.create_user(
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                role=Utilisateur.Role.CONSEILLER,
            )
            return ProfilConseiller.objects.create(
                utilisateur=user,
                specialite=data['specialite'],
                biographie=data['biographie'],
            )
        user = self.instance.utilisateur
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        if data.get('password'):
            user.set_password(data['password'])
        user.role = Utilisateur.Role.CONSEILLER
        user.save()
        self.instance.specialite = data['specialite']
        self.instance.biographie = data['biographie']
        self.instance.save()
        return self.instance


class CandidatStatutForm(forms.Form):
    is_active = forms.BooleanField(
        label='Compte actif',
        required=False,
        help_text='Decocher pour suspendre l acces du candidat.',
    )

    def __init__(self, *args, utilisateur=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.utilisateur = utilisateur
        if utilisateur is not None:
            self.fields['is_active'].initial = utilisateur.is_active
        styliser(self)
