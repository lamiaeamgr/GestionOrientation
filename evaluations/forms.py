from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator

from .models import QuestionEvaluation


class VerificationEmailForm(forms.Form):
    email = forms.EmailField(
        label='Votre adresse email ENSI',
        help_text=(
            "Utilisee uniquement pour verifier votre eligibilite. "
            "Elle n'est jamais stockee ni associee a vos reponses."
        ),
        widget=forms.EmailInput(attrs={'placeholder': 'prenom.nom@ensi-uma.tn'}),
    )


class ReponseCampagneForm(forms.Form):
    """Valide les notes et commentaires d'une campagne d'evaluation."""

    def __init__(self, *args, questions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = list(questions or [])
        for question in self.questions:
            nom = f'question_{question.id}'
            if question.type_question == QuestionEvaluation.TypeQuestion.NOTE:
                self.fields[nom] = forms.IntegerField(
                    label=question.texte,
                    min_value=1,
                    max_value=5,
                    validators=[MinValueValidator(1), MaxValueValidator(5)],
                    error_messages={
                        'required': 'Veuillez attribuer une note de 1 a 5.',
                    },
                )
            else:
                self.fields[nom] = forms.CharField(
                    label=question.texte,
                    required=False,
                    widget=forms.Textarea(attrs={'rows': 3}),
                )

    def details(self):
        resultats = []
        for question in self.questions:
            valeur = self.cleaned_data[f'question_{question.id}']
            if question.type_question == QuestionEvaluation.TypeQuestion.NOTE:
                resultats.append((question, int(valeur), ''))
            else:
                resultats.append((question, None, (valeur or '').strip()))
        return resultats

