from django.contrib import admin

from .models import DisponibiliteConseiller, ProfilConseiller, RendezVous


class DisponibiliteInline(admin.TabularInline):
    model = DisponibiliteConseiller
    extra = 1


@admin.register(ProfilConseiller)
class ProfilConseillerAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'specialite')
    search_fields = ('utilisateur__email', 'utilisateur__last_name')
    inlines = [DisponibiliteInline]


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('candidat', 'conseiller', 'date_rendez_vous', 'statut')
    list_filter = ('statut', 'date_rendez_vous')
    search_fields = (
        'candidat__utilisateur__email',
        'conseiller__utilisateur__email',
    )


admin.site.register(DisponibiliteConseiller)
