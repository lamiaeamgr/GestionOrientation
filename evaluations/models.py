from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Enseignant(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f'{self.prenom} {self.nom}'.strip()


class Module(models.Model):
    nom = models.CharField(max_length=150)
    code = models.CharField(max_length=20, unique=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f'{self.code} - {self.nom}'


class GroupeEtudiant(models.Model):
    nom = models.CharField(max_length=100)
    annee_universitaire = models.CharField(max_length=20, help_text='Ex. : 2025-2026')

    class Meta:
        verbose_name = "groupe d'etudiants"
        ordering = ['annee_universitaire', 'nom']

    def __str__(self):
        return f'{self.nom} ({self.annee_universitaire})'


class CampagneEvaluation(models.Model):
    class Statut(models.TextChoices):
        BROUILLON = 'brouillon', 'Brouillon'
        PROGRAMMEE = 'programmee', 'Programmee'
        ACTIVE = 'active', 'Active'
        FERMEE = 'fermee', 'Fermee'

    titre = models.CharField(max_length=200)
    enseignant = models.ForeignKey(
        Enseignant, on_delete=models.CASCADE, related_name='campagnes'
    )
    module = models.ForeignKey(
        Module, on_delete=models.CASCADE, related_name='campagnes'
    )
    groupe = models.ForeignKey(
        GroupeEtudiant, on_delete=models.CASCADE, related_name='campagnes'
    )
    semestre = models.CharField(max_length=20, blank=True)
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.BROUILLON
    )
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "campagne d'evaluation"
        ordering = ['-date_debut']

    def __str__(self):
        return f'{self.titre} - {self.module} / {self.enseignant}'

    @property
    def est_ouverte(self):
        """La campagne accepte des reponses : statut actif et dans la fenetre de dates."""
        if self.statut != self.Statut.ACTIVE:
            return False
        now = timezone.now()
        if self.date_debut and now < self.date_debut:
            return False
        if self.date_fin and now > self.date_fin:
            return False
        return True


class QuestionEvaluation(models.Model):
    class TypeQuestion(models.TextChoices):
        NOTE = 'note', 'Note (1 a 5)'
        TEXTE = 'texte', 'Texte libre'

    campagne = models.ForeignKey(
        CampagneEvaluation, on_delete=models.CASCADE, related_name='questions'
    )
    texte = models.CharField(max_length=300)
    type_question = models.CharField(
        max_length=10, choices=TypeQuestion.choices, default=TypeQuestion.NOTE
    )
    ordre = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordre']

    def __str__(self):
        return self.texte[:80]


class EvaluateurAutorise(models.Model):
    """Liste blanche : empreinte HMAC de l'email, jamais l'email en clair."""

    campagne = models.ForeignKey(
        CampagneEvaluation, on_delete=models.CASCADE, related_name='evaluateurs_autorises'
    )
    identifiant_anonyme = models.CharField(max_length=64, db_index=True)

    class Meta:
        verbose_name = 'evaluateur autorise'
        unique_together = [('campagne', 'identifiant_anonyme')]

    def __str__(self):
        return f'{self.campagne} : {self.identifiant_anonyme[:12]}...'


class ReponseEvaluation(models.Model):
    """Reponse anonyme : seule l'empreinte est conservee pour garantir l'unicite."""

    campagne = models.ForeignKey(
        CampagneEvaluation, on_delete=models.CASCADE, related_name='reponses'
    )
    identifiant_anonyme = models.CharField(max_length=64, db_index=True)
    date_soumission = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "reponse d'evaluation"
        unique_together = [('campagne', 'identifiant_anonyme')]

    def __str__(self):
        return f'Reponse anonyme {self.identifiant_anonyme[:12]}... ({self.campagne})'


class ReponseQuestionEvaluation(models.Model):
    reponse = models.ForeignKey(
        ReponseEvaluation, on_delete=models.CASCADE, related_name='details'
    )
    question = models.ForeignKey(QuestionEvaluation, on_delete=models.CASCADE)
    note = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    reponse_texte = models.TextField(blank=True)

    class Meta:
        verbose_name = "reponse a une question d'evaluation"
        unique_together = [('reponse', 'question')]

    def __str__(self):
        return f'{self.question} : {self.note or self.reponse_texte[:30]}'
