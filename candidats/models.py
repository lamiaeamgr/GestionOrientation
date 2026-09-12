from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Matiere(models.Model):
    nom = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'matiere'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class CentreInteret(models.Model):
    class Categorie(models.TextChoices):
        DOMAINE = 'domaine', "Domaine d'interet"
        ACTIVITE = 'activite', "Preference d'activite"

    nom = models.CharField(max_length=100)
    categorie = models.CharField(max_length=20, choices=Categorie.choices, default=Categorie.DOMAINE)

    class Meta:
        verbose_name = "centre d'interet"
        ordering = ['categorie', 'nom']
        unique_together = [('nom', 'categorie')]

    def __str__(self):
        return self.nom


class ProfilCandidat(models.Model):
    class NiveauEntree(models.TextChoices):
        BAC = 'bac', 'Baccalaureat'
        BAC2 = 'bac2', 'Bac+2'
        BAC3 = 'bac3', 'Bac+3'

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profil_candidat'
    )
    niveau_entree = models.CharField(
        max_length=10, choices=NiveauEntree.choices, blank=True
    )
    ville = models.CharField(max_length=100, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    profil_complete = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'profil candidat'

    def __str__(self):
        return f'Profil de {self.utilisateur}'


class ProfilAcademique(models.Model):
    """Dossier academique du candidat ; les champs utiles dependent du niveau d'entree."""

    class TypeDiplomeBac(models.TextChoices):
        MATH = 'math', 'Bac Mathematiques'
        SCIENCES = 'sciences', 'Bac Sciences experimentales'
        TECHNIQUE = 'technique', 'Bac Sciences techniques'
        INFO = 'informatique', 'Bac Informatique'
        ECO = 'eco', 'Bac Economie et Gestion'
        LETTRES = 'lettres', 'Bac Lettres'
        SPORT = 'sport', 'Bac Sport'
        AUTRE = 'autre', 'Autre'

    class TypeDiplomeBac2(models.TextChoices):
        BTS = 'bts', 'BTS'
        DUT = 'dut', 'DUT'
        DEUG = 'deug', 'DEUG'
        DEUST = 'deust', 'DEUST'
        CPGE = 'cpge', 'CPGE'
        AUTRE = 'autre', 'Autre'

    class TypeDiplomeBac3(models.TextChoices):
        LICENCE = 'licence', 'Licence'
        BACHELOR = 'bachelor', 'Bachelor'
        LICENCE_PRO = 'licence_pro', 'Licence professionnelle'
        AUTRE = 'autre', 'Autre'

    profil = models.OneToOneField(
        ProfilCandidat, on_delete=models.CASCADE, related_name='academique'
    )
    type_diplome = models.CharField(max_length=30, blank=True)
    specialite = models.CharField(max_length=150, blank=True)
    etablissement = models.CharField(max_length=200, blank=True)
    ville_etablissement = models.CharField(max_length=100, blank=True)
    annee_obtention = models.PositiveIntegerField(null=True, blank=True)
    moyenne_generale = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    moyenne_annee_1 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    moyenne_annee_2 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    moyenne_annee_3 = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )
    modules_principaux = models.TextField(
        blank=True, help_text='Modules principaux suivis (un par ligne).'
    )

    class Meta:
        verbose_name = 'profil academique'

    def __str__(self):
        return f'Dossier academique de {self.profil.utilisateur}'


class NoteAcademique(models.Model):
    academique = models.ForeignKey(
        ProfilAcademique, on_delete=models.CASCADE, related_name='notes'
    )
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, related_name='notes')
    note = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(20)],
    )

    class Meta:
        verbose_name = 'note academique'
        unique_together = [('academique', 'matiere')]

    def __str__(self):
        return f'{self.matiere} : {self.note}/20'


class InteretCandidat(models.Model):
    profil = models.ForeignKey(
        ProfilCandidat, on_delete=models.CASCADE, related_name='interets'
    )
    interet = models.ForeignKey(
        CentreInteret, on_delete=models.CASCADE, related_name='candidats'
    )

    class Meta:
        verbose_name = "interet du candidat"
        unique_together = [('profil', 'interet')]

    def __str__(self):
        return f'{self.profil} - {self.interet}'
