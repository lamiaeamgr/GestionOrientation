from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count
from django.shortcuts import redirect, render
from django.utils import timezone

from candidats.models import ProfilCandidat
from conseil.models import RendezVous
from evaluations.models import CampagneEvaluation, ReponseQuestionEvaluation
from orientation.models import RecommandationFormation, TentativeQuestionnaire


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
        return redirect('dashboard:admin')
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


def _est_admin(user):
    return user.is_authenticated and user.est_admin


@login_required
@user_passes_test(_est_admin)
def admin_dashboard(request):
    """Tableau de bord administrateur : indicateurs cles."""
    nb_candidats = ProfilCandidat.objects.count()
    nb_profils_complets = ProfilCandidat.objects.filter(profil_complete=True).count()
    nb_questionnaires = TentativeQuestionnaire.objects.filter(
        statut=TentativeQuestionnaire.Statut.TERMINE
    ).count()
    nb_rdv = RendezVous.objects.filter(
        statut=RendezVous.Statut.CONFIRME
    ).count()

    repartition = list(
        RecommandationFormation.objects
        .values('formation__nom')
        .annotate(nb=Count('id'), score_moyen=Avg('score_final'))
        .order_by('-nb')[:10]
    )
    # Filiere la mieux classee par recommandation
    top_filiere = list(
        RecommandationFormation.objects
        .values('formation__nom')
        .annotate(nb=Count('id'), score_moyen=Avg('score_final'))
        .order_by('-score_moyen')[:5]
    )

    campagnes = CampagneEvaluation.objects.annotate(
        nb_reponses=Count('reponses')
    ).select_related('enseignant', 'module')[:10]

    stats_eval = list(
        ReponseQuestionEvaluation.objects
        .filter(note__isnull=False)
        .values('reponse__campagne__titre')
        .annotate(moyenne=Avg('note'), total=Count('id'))
        .order_by('-total')[:10]
    )

    return render(request, 'dashboard/admin.html', {
        'nb_candidats': nb_candidats,
        'nb_profils_complets': nb_profils_complets,
        'nb_questionnaires': nb_questionnaires,
        'nb_rdv': nb_rdv,
        'repartition': repartition,
        'top_filiere': top_filiere,
        'campagnes': campagnes,
        'stats_eval': stats_eval,
    })
