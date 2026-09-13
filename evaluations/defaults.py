from .models import QuestionEvaluation

QUESTIONS_DEFAUT = [
    ('Qualite des explications', QuestionEvaluation.TypeQuestion.NOTE),
    ('Maitrise du sujet', QuestionEvaluation.TypeQuestion.NOTE),
    ('Disponibilite', QuestionEvaluation.TypeQuestion.NOTE),
    ('Interaction avec les etudiants', QuestionEvaluation.TypeQuestion.NOTE),
    ('Respect du programme', QuestionEvaluation.TypeQuestion.NOTE),
    ('Qualite des supports', QuestionEvaluation.TypeQuestion.NOTE),
    ('Satisfaction globale', QuestionEvaluation.TypeQuestion.NOTE),
    ('Points positifs (facultatif)', QuestionEvaluation.TypeQuestion.TEXTE),
    ('Points a ameliorer (facultatif)', QuestionEvaluation.TypeQuestion.TEXTE),
]


def creer_questions_defaut(campagne):
    if campagne.questions.exists():
        return
    for ordre, (texte, type_question) in enumerate(QUESTIONS_DEFAUT, start=1):
        QuestionEvaluation.objects.create(
            campagne=campagne,
            texte=texte,
            type_question=type_question,
            ordre=ordre,
        )
