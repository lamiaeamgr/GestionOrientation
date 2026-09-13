from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils import timezone

from conseil.models import RendezVous
from orientation.models import TentativeQuestionnaire


def accueil_public(request):
    """Page d'accueil publique."""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'dashboard/accueil.html')


@login_required
def home(request):
    """Redirige vers le tableau de bord adapte au role."""
    user = request.user
    if user.est_admin:
        return redirect('administration:accueil')
    if user.est_conseiller:
        return redirect('conseil:espace')
    return redirect('dashboard:candidat')


@login_required
def candidat(request):
    if not request.user.est_candidat:
        return redirect('dashboard:home')
    profil = getattr(request.user, 'profil_candidat', None)

    progression = 0
    academique = None
    interets = []
    derniere_recommandation = None
    rdvs_a_venir = []
    tentatives = []

    if profil:
        academique = getattr(profil, 'academique', None)
        interets = profil.interets.select_related('interet')
        # Progression : profil (40) + interets (20) + questionnaire (40)
        if profil.profil_complete:
            progression += 40
        if interets.exists():
            progression += 20
        tentatives = list(profil.tentatives.all())
        if any(t.statut == TentativeQuestionnaire.Statut.TERMINE for t in tentatives):
            progression += 40
        derniere_recommandation = profil.recommandations.prefetch_related(
            'lignes__formation'
        ).first()
        rdvs_a_venir = profil.rendez_vous.filter(
            statut=RendezVous.Statut.CONFIRME,
            date_rendez_vous__gte=timezone.now(),
        ).select_related('conseiller__utilisateur')

    return render(request, 'dashboard/candidat.html', {
        'profil': profil,
        'academique': academique,
        'interets': interets,
        'progression': progression,
        'recommandation': derniere_recommandation,
        'rdvs_a_venir': rdvs_a_venir,
        'tentatives': tentatives,
    })


