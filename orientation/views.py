from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .engine import generer_recommandation
from .models import (
    Question,
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
    if not profil.profil_complete:
        messages.warning(
            request,
            "Completez d'abord votre dossier academique avant le questionnaire.",
        )
        return redirect('candidats:profil')
    questionnaire = (
        Questionnaire.objects.filter(est_actif=True).order_by('-version').first()
    )
    if questionnaire is None:
        messages.error(request, "Aucun questionnaire actif n'est disponible.")
        return redirect('dashboard:home')
    tentative = TentativeQuestionnaire.objects.create(
        profil=profil, questionnaire=questionnaire
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

    questions = tentative.questionnaire.questions.prefetch_related('options')

    if request.method == 'POST':
        valide = True
        reponses_a_creer = []
        for question in questions:
            champ = f'question_{question.id}'
            if question.type_question == Question.TypeQuestion.CHOIX_MULTIPLE:
                ids = request.POST.getlist(champ)
            else:
                valeur = request.POST.get(champ)
                ids = [valeur] if valeur else []
            ids_valides = [
                int(i) for i in ids
                if i.isdigit() and question.options.filter(pk=int(i)).exists()
            ]
            if not ids_valides:
                valide = False
                break
            for option_id in ids_valides:
                reponses_a_creer.append(
                    ReponseCandidat(
                        tentative=tentative, question=question, option_id=option_id
                    )
                )
        if not valide:
            messages.error(request, 'Veuillez repondre a toutes les questions.')
        else:
            with transaction.atomic():
                ReponseCandidat.objects.bulk_create(reponses_a_creer)
                tentative.statut = TentativeQuestionnaire.Statut.TERMINE
                tentative.date_soumission = timezone.now()
                tentative.save(update_fields=['statut', 'date_soumission'])
                recommandation = generer_recommandation(profil, tentative)
            messages.success(request, 'Questionnaire termine. Voici vos recommandations.')
            return redirect('orientation:resultats', pk=recommandation.pk)

    return render(request, 'orientation/questionnaire.html', {
        'tentative': tentative,
        'questions': questions,
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
