from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from candidats.models import Matiere


class Formation(models.Model):
    class Niveau(models.TextChoices):
        PREPA = 'prepa', 'Cycle preparatoire'
        INGENIEUR = 'ingenieur', 'Cycle ingenieur'
        LICENCE = 'licence', 'Licence'
        MASTER = 'master', 'Master'

    nom = models.CharField(max_length=200)
    domaine = models.CharField('pole / domaine', max_length=150)
    niveau = models.CharField(max_length=20, choices=Niveau.choices)
    parcours = models.CharField(
        max_length=150, blank=True,
        help_text='Ex. : Prepa + Cycle Ingenieur, Licence + Master, admission parallele'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='specialisations',
        help_text='Filiere parente (ex. : Genie Informatique pour Web & Mobile).',
    )
    description = models.TextField(blank=True)
    conditions_admission = models.TextField(blank=True)
    competences_recherchees = models.TextField(blank=True)
    matieres_importantes = models.ManyToManyField(
        Matiere, blank=True, related_name='formations'
    )
    class Reconnaissance(models.TextChoices):
        RECONNUE = 'reconnue', "Reconnue par l'Etat"
        ACCREDITEE = 'accreditee', 'Accreditee uniquement'

    debouches = models.TextField(blank=True)
    reconnaissance = models.CharField(
        max_length=20,
        choices=Reconnaissance.choices,
        default=Reconnaissance.RECONNUE,
        help_text=(
            "Projet public : formations reconnues par l'Etat. "
            "Projet prive : les formations accreditees sont aussi proposees."
        ),
    )
    est_active = models.BooleanField(default=True)
    image = models.ImageField(
        'image de couverture',
        upload_to='formations/',
        blank=True,
        help_text='Affichee sur le catalogue candidat et dans l administration.',
    )

    class Meta:
        verbose_name = 'formation'
        ordering = ['domaine', 'nom']

    def __str__(self):
        return self.nom


class PrerequisFormation(models.Model):
    formation = models.ForeignKey(
        Formation, on_delete=models.CASCADE, related_name='prerequis'
    )
    matiere = models.ForeignKey(
        Matiere, on_delete=models.CASCADE, related_name='prerequis'
    )
    note_minimale = models.DecimalField(
        max_digits=5, decimal_places=2, default=10,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    poids = models.PositiveIntegerField(
        default=1, help_text='Importance relative de la matiere pour cette formation.'
    )

    class Meta:
        verbose_name = 'prerequis de formation'
        unique_together = [('formation', 'matiere')]

    def __str__(self):
        return f'{self.formation} : {self.matiere} >= {self.note_minimale} (poids {self.poids})'
