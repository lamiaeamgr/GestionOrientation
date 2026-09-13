from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .ai import appliquer_personnalisation, generer_questionnaire_personnalise
from .engine import generer_recommandation
from .forms import QuestionnaireReponsesForm
from .models import (
    Questionnaire,
    Recommandation,
    ReponseCandidat,
    TentativeQuestionnaire,
)


def _profil_ou_redirection(request):
    profil = getattr(request.user, 'profil_candidat', None)
    if profil is None or not request.user.est_candidat:
        messages.error(request, "Cette page est reservee aux candidats.")
        return None
    return profil


@login_required
def demarrer(request):
    """Lance une nouvelle tentative si le profil academique est complet."""
    profil = _profil_ou_redirection(request)
    if profil is None:
        return redirect('dashboard:home')
    if not profil.profil_complete or not profil.objectif:
        messages.warning(
            request,
            "Indiquez d'abord votre projet (public ou prive) et completez votre dossier.",
        )
        return redirect('candidats:profil')
    questionnaire = (
        Questionnaire.objects.filter(est_actif=True).order_by('-version').first()
    )
    if questionnaire is None:
        messages.error(request, "Aucun questionnaire actif n'est disponible.")
        return redirect('dashboard:home')
    questions = list(questionnaire.questions.prefetch_related('options'))
    perso = generer_questionnaire_personnalise(profil, questions)
    tentative = TentativeQuestionnaire.objects.create(
        profil=profil,
        questionnaire=questionnaire,
        personnalisation=perso or {},
    )
    return redirect('orientation:passer', pk=tentative.pk)


@login_required
def passer(request, pk):
    tentative = get_object_or_404(
        TentativeQuestionnaire.objects.select_related('questionnaire', 'profil'),
        pk=pk,
    )
    profil = _profil_ou_redirection(request)
    if profil is None or tentative.profil_id != profil.id:
        messages.error(request, 'Acces non autorise.')
        return redirect('dashboard:home')
    if tentative.statut == TentativeQuestionnaire.Statut.TERMINE:
        return redirect('orientation:resultats', pk=tentative.recommandation.pk)

    questions = list(tentative.questionnaire.questions.prefetch_related('options'))
    questions, intro_ia = appliquer_personnalisation(
        questions, tentative.personnalisation
    )

    if request.method == 'POST':
        form = QuestionnaireReponsesForm(request.POST, questions=questions)
        if form.is_valid():
            with transaction.atomic():
                ReponseCandidat.objects.bulk_create(form.reponses_pour(tentative))
                tentative.statut = TentativeQuestionnaire.Statut.TERMINE
                tentative.date_soumission = timezone.now()
                tentative.save(update_fields=['statut', 'date_soumission'])
                recommandation = generer_recommandation(profil, tentative)
            messages.success(request, 'Questionnaire termine. Voici vos recommandations.')
            return redirect('orientation:resultats', pk=recommandation.pk)
        messages.error(request, 'Veuillez repondre a toutes les questions.')
    else:
        form = QuestionnaireReponsesForm(questions=questions)

    return render(request, 'orientation/questionnaire.html', {
        'tentative': tentative,
        'questions': questions,
        'form': form,
        'intro_ia': intro_ia,
    })


@login_required
def resultats(request, pk):
    recommandation = get_object_or_404(
        Recommandation.objects.select_related('profil__utilisateur')
        .prefetch_related('lignes__formation'),
        pk=pk,
    )
    if not (
        request.user.est_admin
        or request.user.est_conseiller
        or recommandation.profil.utilisateur_id == request.user.id
    ):
        messages.error(request, 'Acces non autorise.')
        return redirect('dashboard:home')
    lignes = list(recommandation.lignes.all())
    return render(request, 'orientation/resultats.html', {
        'recommandation': recommandation,
        'lignes': lignes,
    })


@login_required
def historique(request):
    profil = _profil_ou_redirection(request)
    if profil is None:
        return redirect('dashboard:home')
    tentatives = profil.tentatives.select_related('questionnaire')
    recommandations = profil.recommandations.prefetch_related('lignes__formation')
    return render(request, 'orientation/historique.html', {
        'tentatives': tentatives,
        'recommandations': recommandations,
    })
