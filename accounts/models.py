from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UtilisateurManager(BaseUserManager):
    """Manager pour un modele utilisateur identifie par email."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Utilisateur.Role.ADMIN)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class Utilisateur(AbstractUser):
    """Utilisateur de la plateforme : candidat, conseiller ou administrateur."""

    class Role(models.TextChoices):
        CANDIDAT = 'candidat', 'Candidat'
        CONSEILLER = 'conseiller', "Conseiller d'orientation"
        ADMIN = 'admin', 'Administrateur'

    username = None
    email = models.EmailField('adresse email', unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CANDIDAT)
    date_creation = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UtilisateurManager()

    class Meta:
        verbose_name = 'utilisateur'
        verbose_name_plural = 'utilisateurs'

    def __str__(self):
        return f'{self.get_full_name() or self.email} ({self.get_role_display()})'

    @property
    def est_candidat(self):
        return self.role == self.Role.CANDIDAT

    @property
    def est_conseiller(self):
        return self.role == self.Role.CONSEILLER

    @property
    def est_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser
