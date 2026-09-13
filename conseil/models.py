from django.conf import settings
from django.db import models
from django.utils import timezone

from candidats.models import ProfilCandidat


class ProfilConseiller(models.Model):
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profil_conseiller'
    )
    specialite = models.CharField("domaine d'accompagnement", max_length=150, blank=True)
    biographie = models.TextField(blank=True)

    class Meta:
        verbose_name = 'profil conseiller'

    def __str__(self):
        return f'Conseiller {self.utilisateur.get_full_name() or self.utilisateur.email}'


class DisponibiliteConseiller(models.Model):
    conseiller = models.ForeignKey(
        ProfilConseiller, on_delete=models.CASCADE, related_name='disponibilites'
    )
    date_heure_debut = models.DateTimeField()
    date_heure_fin = models.DateTimeField()
    est_disponible = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'disponibilite conseiller'
        ordering = ['date_heure_debut']
        constraints = [
            models.CheckConstraint(
                condition=models.Q(date_heure_fin__gt=models.F('date_heure_debut')),
                name='conseil_dispo_fin_apres_debut',
            ),
        ]

    def __str__(self):
        return f'{self.conseiller} : {self.date_heure_debut:%d/%m/%Y %H:%M}'

    @property
    def est_passee(self):
        return self.date_heure_debut < timezone.now()

    @property
    def est_reservable(self):
        return (
            self.est_disponible
            and not self.est_passee
            and not hasattr(self, 'rendez_vous')
        )


class RendezVous(models.Model):
    class Statut(models.TextChoices):
        CONFIRME = 'confirme', 'Confirme'
        ANNULE = 'annule', 'Annule'
        TERMINE = 'termine', 'Termine'

    candidat = models.ForeignKey(
        ProfilCandidat, on_delete=models.CASCADE, related_name='rendez_vous'
    )
    conseiller = models.ForeignKey(
        ProfilConseiller, on_delete=models.CASCADE, related_name='rendez_vous'
    )
    disponibilite = models.OneToOneField(
        DisponibiliteConseiller, on_delete=models.CASCADE,
        related_name='rendez_vous', null=True, blank=True,
        help_text='Un creneau ne peut etre reserve qu une seule fois.',
    )
    date_rendez_vous = models.DateTimeField()
    motif = models.TextField(blank=True)
    statut = models.CharField(
        max_length=20, choices=Statut.choices, default=Statut.CONFIRME
    )
    note_conseiller = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'rendez-vous'
        ordering = ['date_rendez_vous']

    def __str__(self):
        return f'RDV {self.candidat} / {self.conseiller} le {self.date_rendez_vous:%d/%m/%Y %H:%M}'
