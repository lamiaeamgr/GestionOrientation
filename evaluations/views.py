from django.contrib import messages
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import VerificationEmailForm
from .models import (
    CampagneEvaluation,
    EvaluateurAutorise,
    QuestionEvaluation,
    ReponseEvaluation,
    ReponseQuestionEvaluation,
)
from .utils import empreinte_email

SESSION_CLE = 'evaluation_eligible'  # {campagne_id: identifiant_anonyme}


def accueil(request):
    """Liste publique des campagnes actuellement ouvertes."""
    campagnes = [
        c for c in CampagneEvaluation.objects.filter(
            statut=CampagneEvaluation.Statut.ACTIVE
        ).select_related('enseignant', 'module', 'groupe')
        if c.est_ouverte
    ]
    return render(request, 'evaluations/accueil.html', {'campagnes': campagnes})


def verifier(request, campagne_id):
    """Etape 1 : verification d'eligibilite par email (jamais stocke)."""
    campagne = get_object_or_404(
        CampagneEvaluation.objects.select_related('enseignant', 'module', 'groupe'),
        pk=campagne_id,
    )
    if not campagne.est_ouverte:
        messages.error(request, "Cette campagne n'accepte pas de reponses actuellement.")
        return redirect('evaluations:accueil')

    if request.method == 'POST':
        form = VerificationEmailForm(request.POST)
        if form.is_valid():
            empreinte = empreinte_email(form.cleaned_data['email'])
            if not EvaluateurAutorise.objects.filter(
                campagne=campagne, identifiant_anonyme=empreinte
            ).exists():
                messages.error(
                    request,
                    "Cette adresse n'est pas autorisee a repondre a cette campagne.",
                )
            elif ReponseEvaluation.objects.filter(
                campagne=campagne, identifiant_anonyme=empreinte
            ).exists():
                messages.warning(
                    request, 'Une reponse a deja ete soumise pour cette campagne.'
                )
            else:
                eligibles = request.session.get(SESSION_CLE, {})
                eligibles[str(campagne.id)] = empreinte
                request.session[SESSION_CLE] = eligibles
                return redirect('evaluations:repondre', campagne_id=campagne.id)
    else:
        form = VerificationEmailForm()
    return render(request, 'evaluations/verifier.html', {
        'campagne': campagne, 'form': form,
    })


def repondre(request, campagne_id):
    """Etape 2 : formulaire anonyme, accessible uniquement apres verification."""
    campagne = get_object_or_404(
        CampagneEvaluation.objects.prefetch_related('questions'),
        pk=campagne_id,
    )
    if not campagne.est_ouverte:
        messages.error(request, "Cette campagne n'accepte plus de reponses.")
        return redirect('evaluations:accueil')

    empreinte = (request.session.get(SESSION_CLE) or {}).get(str(campagne.id))
    if not empreinte:
        return redirect('evaluations:verifier', campagne_id=campagne.id)

    questions = list(campagne.questions.all())

    if request.method == 'POST':
        valide = True
        details = []
        for question in questions:
            if question.type_question == QuestionEvaluation.TypeQuestion.NOTE:
                valeur = request.POST.get(f'question_{question.id}')
                if not valeur or not valeur.isdigit() or not (1 <= int(valeur) <= 5):
                    valide = False
                    break
                details.append((question, int(valeur), ''))
            else:
                texte = request.POST.get(f'question_{question.id}', '').strip()
                details.append((question, None, texte))
        if not valide:
            messages.error(request, 'Veuillez attribuer une note de 1 a 5 a chaque critere.')
        else:
            try:
                with transaction.atomic():
                    reponse = ReponseEvaluation.objects.create(
                        campagne=campagne, identifiant_anonyme=empreinte
                    )
                    ReponseQuestionEvaluation.objects.bulk_create([
                        ReponseQuestionEvaluation(
                            reponse=reponse, question=q, note=n, reponse_texte=t
                        )
                        for q, n, t in details
                    ])
            except IntegrityError:
                messages.warning(
                    request, 'Une reponse a deja ete soumise pour cette campagne.'
                )
                return redirect('evaluations:accueil')
            # On retire l'autorisation de la session
            eligibles = request.session.get(SESSION_CLE, {})
            eligibles.pop(str(campagne.id), None)
            request.session[SESSION_CLE] = eligibles
            return render(request, 'evaluations/remerciement.html', {'campagne': campagne})

    return render(request, 'evaluations/repondre.html', {
        'campagne': campagne,
        'questions': questions,
        'echelle': range(1, 6),
    })
