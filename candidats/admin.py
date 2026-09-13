from django.contrib import admin

from .models import (
    CentreInteret,
    InteretCandidat,
    Matiere,
    NoteAcademique,
    ProfilAcademique,
    ProfilCandidat,
)


class NoteAcademiqueInline(admin.TabularInline):
    model = NoteAcademique
    extra = 1


class InteretCandidatInline(admin.TabularInline):
    model = InteretCandidat
    extra = 1


class ProfilAcademiqueInline(admin.StackedInline):
    model = ProfilAcademique
    can_delete = False


@admin.register(ProfilCandidat)
class ProfilCandidatAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'niveau_entree', 'objectif', 'ville', 'profil_complete')
    list_filter = ('niveau_entree', 'objectif', 'profil_complete')
    search_fields = ('utilisateur__email', 'utilisateur__first_name', 'utilisateur__last_name')
    inlines = [ProfilAcademiqueInline, InteretCandidatInline]


@admin.register(ProfilAcademique)
class ProfilAcademiqueAdmin(admin.ModelAdmin):
    list_display = ('profil', 'type_diplome', 'specialite', 'annee_obtention', 'moyenne_generale')
    inlines = [NoteAcademiqueInline]


admin.site.register(Matiere)
admin.site.register(CentreInteret)
admin.site.register(NoteAcademique)
admin.site.register(InteretCandidat)
