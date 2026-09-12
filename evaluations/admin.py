from django.contrib import admin, messages
from django.db.models import Avg, Count

from .models import (
    CampagneEvaluation,
    Enseignant,
    EvaluateurAutorise,
    GroupeEtudiant,
    Module,
    QuestionEvaluation,
    ReponseEvaluation,
    ReponseQuestionEvaluation,
)
from .utils import empreinte_email


class QuestionEvaluationInline(admin.TabularInline):
    model = QuestionEvaluation
    extra = 1


class EvaluateurAutoriseInline(admin.TabularInline):
    model = EvaluateurAutorise
    extra = 1
    verbose_name = 'evaluateur autorise (empreinte)'
    verbose_name_plural = 'evaluateurs autorises (empreintes)'


@admin.action(description='Importer des emails dans la liste blanche (un par ligne)')
def importer_emails(modeladmin, request, queryset):
    """Action disponible via la vue detail : voir importer_liste_blanche."""
    messages.info(request, 'Utilisez le bouton "Importer la liste blanche" sur la campagne.')


@admin.register(CampagneEvaluation)
class CampagneEvaluationAdmin(admin.ModelAdmin):
    list_display = (
        'titre', 'module', 'enseignant', 'groupe', 'semestre',
        'statut', 'date_debut', 'date_fin', 'nb_reponses',
    )
    list_filter = ('statut', 'semestre', 'groupe')
    inlines = [QuestionEvaluationInline, EvaluateurAutoriseInline]
    change_form_template = 'admin/evaluations/campagne_change_form.html'

    def nb_reponses(self, obj):
        return obj.reponses.count()
    nb_reponses.short_description = 'Reponses'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        campagne = self.get_object(request, object_id)
        if campagne:
            extra_context['stats'] = self._stats_agregees(campagne)
        return super().change_view(request, object_id, form_url, extra_context)

    def _stats_agregees(self, campagne):
        return (
            ReponseQuestionEvaluation.objects
            .filter(reponse__campagne=campagne, note__isnull=False)
            .values('question__texte')
            .annotate(moyenne=Avg('note'), total=Count('id'))
            .order_by('question__ordre')
        )

    def response_change(self, request, obj):
        # Import de la liste blanche depuis le champ "emails" du formulaire custom
        emails = request.POST.get('emails_import', '')
        if emails:
            crees = 0
            for ligne in emails.splitlines():
                ligne = ligne.strip()
                if not ligne:
                    continue
                _, created = EvaluateurAutorise.objects.get_or_create(
                    campagne=obj, identifiant_anonyme=empreinte_email(ligne)
                )
                crees += created
            self.message_user(
                request, f'{crees} empreinte(s) ajoutee(s) a la liste blanche.',
                messages.SUCCESS,
            )
        return super().response_change(request, obj)


@admin.register(ReponseEvaluation)
class ReponseEvaluationAdmin(admin.ModelAdmin):
    """Lecture agregee uniquement : pas d'export nominatif possible."""

    list_display = ('campagne', 'identifiant_tronque', 'date_soumission')
    list_filter = ('campagne',)
    readonly_fields = ('campagne', 'identifiant_anonyme', 'date_soumission')

    def identifiant_tronque(self, obj):
        return f'{obj.identifiant_anonyme[:12]}...'
    identifiant_tronque.short_description = 'Identifiant (tronque)'

    def has_add_permission(self, request):
        return False


admin.site.register(Enseignant)
admin.site.register(Module)
admin.site.register(GroupeEtudiant)
admin.site.register(QuestionEvaluation)
admin.site.register(EvaluateurAutorise)
admin.site.register(ReponseQuestionEvaluation)
