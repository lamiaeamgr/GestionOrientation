from django.contrib import admin

from .models import Formation, PrerequisFormation


class PrerequisInline(admin.TabularInline):
    model = PrerequisFormation
    extra = 1


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ('nom', 'domaine', 'niveau', 'parcours', 'parent', 'est_active')
    list_filter = ('niveau', 'domaine', 'est_active')
    search_fields = ('nom', 'domaine')
    filter_horizontal = ('matieres_importantes',)
    inlines = [PrerequisInline]


admin.site.register(PrerequisFormation)
