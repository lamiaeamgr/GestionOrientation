from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from candidats.models import ProfilCandidat
from formations.models import Formation


class Questionnaire(models.Model):
    titre = models.CharField(max_length=200)
    version = models.PositiveIntegerField(default=1)
    est_actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = "questionnaire d'orientation"

    def __str__(self):
        return f'{self.titre} (v{self.version})'


class Question(models.Model):
    class TypeQuestion(models.TextChoices):
        CHOIX_UNIQUE = 'choix_unique', 'Choix unique'
        CHOIX_MULTIPLE = 'choix_multiple', 'Choix multiple'

    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.CASCADE, related_name='questions'
    )
    texte = models.TextField()
    ordre = models.PositiveIntegerField(default=0)
    type_question = models.CharField(
        max_length=20, choices=TypeQuestion.choices, default=TypeQuestion.CHOIX_UNIQUE
    )

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return self.texte[:80]


class OptionReponse(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='options'
    )
    texte = models.CharField(max_length=300)

    class Meta:
        verbose_name = "option de reponse"

    def __str__(self):
        return self.texte[:80]


class PonderationOptionFormation(models.Model):
    """Poids accorde a une formation lorsque l'option est choisie."""

    option = models.ForeignKey(
        OptionReponse, on_delete=models.CASCADE, related_name='ponderations'
    )
    formation = models.ForeignKey(
        Formation, on_delete=models.CASCADE, related_name='ponderations_options'
    )
    poids = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'ponderation option / formation'
        unique_together = [('option', 'formation')]

    def __str__(self):
        return f'{self.option} -> {self.formation} ({self.poids})'


class TentativeQuestionnaire(models.Model):
    class Statut(models.TextChoices):
        EN_COURS = 'en_cours', 'En cours'
        TERMINE = 'termine', 'Termine'

    profil = models.ForeignKey(
        ProfilCandidat, on_delete=models.CASCADE, related_name='tentatives'
    )
    questionnaire = models.ForeignKey(
        Questionnaire, on_delete=models.CASCADE, related_name='tentatives'
    )
    date_debut = models.DateTimeField(auto_now_add=True)
    date_soumission = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.EN_COURS
    )

    class Meta:
        verbose_name = 'tentative de questionnaire'
        ordering = ['-date_debut']

    def __str__(self):
        return f'{self.profil} - {self.questionnaire} ({self.get_statut_display()})'


class ReponseCandidat(models.Model):
    tentative = models.ForeignKey(
        TentativeQuestionnaire, on_delete=models.CASCADE, related_name='reponses'
    )
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option = models.ForeignKey(OptionReponse, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'reponse du candidat'
        unique_together = [('tentative', 'question', 'option')]

    def __str__(self):
        return f'{self.question} : {self.option}'


class Recommandation(models.Model):
    """Resultat global d'une tentative : classement des formations."""

    profil = models.ForeignKey(
        ProfilCandidat, on_delete=models.CASCADE, related_name='recommandations'
    )
    tentative = models.OneToOneField(
        TentativeQuestionnaire, on_delete=models.CASCADE,
        related_name='recommandation', null=True, blank=True,
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f'Recommandation de {self.profil} ({self.date_creation:%d/%m/%Y})'


class RecommandationFormation(models.Model):
    recommandation = models.ForeignKey(
        Recommandation, on_delete=models.CASCADE, related_name='lignes'
    )
    formation = models.ForeignKey(
        Formation, on_delete=models.CASCADE, related_name='recommandations'
    )
    score_academique = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    score_interets = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    score_questionnaire = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    score_final = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    explication = models.JSONField(
        default=dict, blank=True,
        help_text='Facteurs ayant contribue au score (pour la transparence).',
    )

    class Meta:
        verbose_name = 'formation recommandee'
        ordering = ['-score_final']
        unique_together = [('recommandation', 'formation')]

    def __str__(self):
        return f'{self.formation} : {self.score_final}%'
