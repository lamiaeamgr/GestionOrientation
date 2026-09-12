from django.contrib import admin

from .models import (
    OptionReponse,
    PonderationOptionFormation,
    Question,
    Questionnaire,
    Recommandation,
    RecommandationFormation,
    ReponseCandidat,
    TentativeQuestionnaire,
)


class PonderationInline(admin.TabularInline):
    model = PonderationOptionFormation
    extra = 1


class OptionInline(admin.TabularInline):
    model = OptionReponse
    extra = 2
    show_change_link = True


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ('titre', 'version', 'est_actif')
    list_filter = ('est_actif',)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('texte', 'questionnaire', 'ordre', 'type_question')
    list_filter = ('questionnaire', 'type_question')
    ordering = ('questionnaire', 'ordre')
    inlines = [OptionInline]


@admin.register(OptionReponse)
class OptionReponseAdmin(admin.ModelAdmin):
    list_display = ('texte', 'question')
    search_fields = ('texte',)
    inlines = [PonderationInline]


class RecommandationFormationInline(admin.TabularInline):
    model = RecommandationFormation
    extra = 0
    readonly_fields = ('score_final',)


@admin.register(Recommandation)
class RecommandationAdmin(admin.ModelAdmin):
    list_display = ('profil', 'date_creation')
    inlines = [RecommandationFormationInline]


admin.site.register(TentativeQuestionnaire)
admin.site.register(ReponseCandidat)
admin.site.register(PonderationOptionFormation)
