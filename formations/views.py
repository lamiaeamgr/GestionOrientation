from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .models import Formation


def liste(request):
    """Catalogue public des formations actives."""
    formations = (
        Formation.objects.filter(est_active=True)
        .select_related('parent')
        .prefetch_related('matieres_importantes')
    )
    domaine = request.GET.get('domaine')
    if domaine:
        formations = formations.filter(domaine=domaine)
    domaines = (
        Formation.objects.filter(est_active=True)
        .values_list('domaine', flat=True).distinct().order_by('domaine')
    )
    return render(request, 'formations/liste.html', {
        'formations': formations,
        'domaines': domaines,
        'domaine_actif': domaine,
    })


def detail(request, pk):
    formation = get_object_or_404(
        Formation.objects.select_related('parent')
        .prefetch_related('matieres_importantes', 'prerequis__matiere', 'specialisations'),
        pk=pk,
    )
    return render(request, 'formations/detail.html', {'formation': formation})


@login_required
def comparer(request):
    """Comparaison cote a cote de plusieurs formations."""
    ids = request.GET.getlist('ids')
    formations = list(
        Formation.objects.filter(pk__in=ids, est_active=True)
        .prefetch_related('matieres_importantes', 'prerequis__matiere')
    )
    if len(formations) < 2:
        messages.info(request, 'Selectionnez au moins deux formations a comparer.')
    scores = {}
    if request.user.est_candidat:
        try:
            derniere = request.user.profil_candidat.recommandations.first()
        except Exception:
            derniere = None
        if derniere:
            scores = {
                ligne.formation_id: ligne.score_final
                for ligne in derniere.lignes.all()
            }
    return render(request, 'formations/comparer.html', {
        'formations': formations,
        'scores': scores,
    })
