from django import forms

from .models import Question, ReponseCandidat


class QuestionnaireReponsesForm(forms.Form):
    """Valide les reponses dynamiques d'une tentative de questionnaire."""

    def __init__(self, *args, questions=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.questions = list(questions or [])
        for question in self.questions:
            nom = f'question_{question.id}'
            choix = [(str(opt.id), opt.texte) for opt in question.options.all()]
            if question.type_question == Question.TypeQuestion.CHOIX_MULTIPLE:
                self.fields[nom] = forms.MultipleChoiceField(
                    choices=choix,
                    widget=forms.CheckboxSelectMultiple,
                    required=True,
                    label=question.texte,
                    error_messages={
                        'required': 'Veuillez selectionner au moins une option.',
                    },
                )
            else:
                self.fields[nom] = forms.ChoiceField(
                    choices=choix,
                    widget=forms.RadioSelect,
                    required=True,
                    label=question.texte,
                    error_messages={
                        'required': 'Veuillez choisir une option.',
                    },
                )

    def reponses_pour(self, tentative):
        objets = []
        for question in self.questions:
            valeurs = self.cleaned_data[f'question_{question.id}']
            if not isinstance(valeurs, (list, tuple)):
                valeurs = [valeurs]
            for option_id in valeurs:
                objets.append(
                    ReponseCandidat(
                        tentative=tentative,
                        question=question,
                        option_id=int(option_id),
                    )
                )
        return objets
