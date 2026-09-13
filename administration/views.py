from django.contrib import messages
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.decorators import admin_requis
from candidats.models import CentreInteret, ProfilCandidat
from conseil.models import ProfilConseiller, RendezVous
from evaluations.defaults import creer_questions_defaut
from evaluations.models import (
    CampagneEvaluation,
    Enseignant,
    EtudiantInterne,
    EvaluateurAutorise,
    GroupeEtudiant,
    Module,
    QuestionEvaluation,
    ReponseQuestionEvaluation,
)
from evaluations.utils import empreinte_email
from formations.models import Formation, PrerequisFormation
from orientation.ai import suggerer_evaluation, suggerer_questionnaire
from orientation.models import (
    OptionReponse,
    PonderationOptionFormation,
    Question,
    Questionnaire,
    RecommandationFormation,
    TentativeQuestionnaire,
)

from .forms import (
    AffectationClasseForm,
    CampagneForm,
    CandidatStatutForm,
    ConseillerForm,
    EnseignantForm,
    EtudiantInterneForm,
    FormationForm,
    GroupeForm,
    InteretForm,
    ModuleForm,
    OptionReponseForm,
    PonderationForm,
    PrerequisForm,
    QuestionEvaluationForm,
    QuestionOrientationForm,
    QuestionnaireForm,
)


@admin_requis
def accueil(request):
    nb_candidats = ProfilCandidat.objects.count()
    nb_profils_complets = ProfilCandidat.objects.filter(profil_complete=True).count()
    nb_questionnaires = TentativeQuestionnaire.objects.filter(
        statut=TentativeQuestionnaire.Statut.TERMINE
    ).count()
    nb_rdv = RendezVous.objects.filter(statut=RendezVous.Statut.CONFIRME).count()

    repartition = list(
        RecommandationFormation.objects
        .values('formation__nom')
        .annotate(nb=Count('id'), score_moyen=Avg('score_final'))
        .order_by('-nb')[:10]
    )
    top_filiere = list(
        RecommandationFormation.objects
        .values('formation__nom')
        .annotate(nb=Count('id'), score_moyen=Avg('score_final'))
        .order_by('-score_moyen')[:5]
    )
    campagnes = CampagneEvaluation.objects.annotate(
        nb_reponses=Count('reponses'),
        nb_autorises=Count('evaluateurs_autorises', distinct=True),
    ).select_related('enseignant', 'module')[:10]
    stats_eval = list(
        ReponseQuestionEvaluation.objects
        .filter(note__isnull=False)
        .values('reponse__campagne_id', 'reponse__campagne__titre')
        .annotate(moyenne=Avg('note'), total=Count('id'))
        .order_by('-total')[:10]
    )
    niveaux = list(
        ProfilCandidat.objects.exclude(niveau_entree='')
        .values('niveau_entree')
        .annotate(nb=Count('id'))
        .order_by('niveau_entree')
    )
    rdv_statuts = list(
        RendezVous.objects.values('statut').annotate(nb=Count('id')).order_by('statut')
    )
    graphiques = {
        'reco_labels': [r['formation__nom'] for r in repartition],
        'reco_values': [r['nb'] for r in repartition],
        'niveaux_labels': [
            dict(ProfilCandidat.NiveauEntree.choices).get(r['niveau_entree'], r['niveau_entree'])
            for r in niveaux
        ],
        'niveaux_values': [r['nb'] for r in niveaux],
        'rdv_labels': [
            dict(RendezVous.Statut.choices).get(r['statut'], r['statut'])
            for r in rdv_statuts
        ],
        'rdv_values': [r['nb'] for r in rdv_statuts],
        'eval_labels': [s['reponse__campagne__titre'] for s in stats_eval],
        'eval_values': [round(float(s['moyenne'] or 0), 2) for s in stats_eval],
        'part_labels': [c.titre for c in campagnes],
        'part_reponses': [c.nb_reponses for c in campagnes],
        'part_autorises': [c.nb_autorises for c in campagnes],
    }
    return render(request, 'administration/accueil.html', {
        'nb_candidats': nb_candidats,
        'nb_profils_complets': nb_profils_complets,
        'nb_questionnaires': nb_questionnaires,
        'nb_rdv': nb_rdv,
        'repartition': repartition,
        'top_filiere': top_filiere,
        'campagnes': campagnes,
        'stats_eval': stats_eval,
        'graphiques': graphiques,
    })


# ---------- Formations ----------

@admin_requis
def formations_liste(request):
    formations = Formation.objects.select_related('parent').order_by('domaine', 'nom')
    return render(request, 'administration/formations_liste.html', {
        'formations': formations,
    })


@admin_requis
def formation_editer(request, pk=None):
    instance = get_object_or_404(Formation, pk=pk) if pk else None
    if request.method == 'POST':
        form = FormationForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            formation = form.save()
            messages.success(request, 'Formation enregistree.')
            return redirect('administration:formation_detail', pk=formation.pk)
    else:
        form = FormationForm(instance=instance)
    return render(request, 'administration/formation_form.html', {
        'form': form,
        'formation': instance,
    })


@admin_requis
def formation_detail(request, pk):
    formation = get_object_or_404(
        Formation.objects.prefetch_related('prerequis__matiere', 'matieres_importantes'),
        pk=pk,
    )
    if request.method == 'POST':
        form = PrerequisForm(request.POST)
        if form.is_valid():
            prerequis = form.save(commit=False)
            prerequis.formation = formation
            if PrerequisFormation.objects.filter(
                formation=formation, matiere=prerequis.matiere
            ).exists():
                messages.error(request, 'Ce prerequis existe deja.')
            else:
                prerequis.save()
                messages.success(request, 'Prerequis ajoute.')
            return redirect('administration:formation_detail', pk=pk)
    else:
        form = PrerequisForm()
    return render(request, 'administration/formation_detail.html', {
        'formation': formation,
        'form': form,
    })


@admin_requis
def formation_supprimer(request, pk):
    formation = get_object_or_404(Formation, pk=pk)
    if request.method == 'POST':
        nom = formation.nom
        formation.delete()
        messages.success(request, f'Formation « {nom} » supprimee.')
        return redirect('administration:formations')
    return render(request, 'administration/confirm_delete.html', {
        'objet': formation,
        'titre': 'Supprimer la formation',
        'retour': 'administration:formations',
    })


@admin_requis
def prerequis_supprimer(request, pk):
    prerequis = get_object_or_404(PrerequisFormation, pk=pk)
    formation_id = prerequis.formation_id
    if request.method == 'POST':
        prerequis.delete()
        messages.success(request, 'Prerequis supprime.')
    return redirect('administration:formation_detail', pk=formation_id)


# ---------- Referentiels evaluations ----------

def _crud_simple(request, model, form_class, template, context_name, retour):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Enregistrement ajoute.')
            return redirect(retour)
    else:
        form = form_class()
    return render(request, template, {
        context_name: model.objects.all(),
        'form': form,
    })


@admin_requis
def enseignants(request):
    return _crud_simple(
        request, Enseignant, EnseignantForm,
        'administration/enseignants.html', 'enseignants',
        'administration:enseignants',
    )


@admin_requis
def enseignant_supprimer(request, pk):
    objet = get_object_or_404(Enseignant, pk=pk)
    if request.method == 'POST':
        objet.delete()
        messages.success(request, 'Enseignant supprime.')
    return redirect('administration:enseignants')


@admin_requis
def modules(request):
    return _crud_simple(
        request, Module, ModuleForm,
        'administration/modules.html', 'modules',
        'administration:modules',
    )


@admin_requis
def module_supprimer(request, pk):
    objet = get_object_or_404(Module, pk=pk)
    if request.method == 'POST':
        objet.delete()
        messages.success(request, 'Module supprime.')
    return redirect('administration:modules')


@admin_requis
def groupes(request):
    return _crud_simple(
        request, GroupeEtudiant, GroupeForm,
        'administration/groupes.html', 'groupes',
        'administration:groupes',
    )


@admin_requis
def groupe_supprimer(request, pk):
    objet = get_object_or_404(GroupeEtudiant, pk=pk)
    if request.method == 'POST':
        objet.delete()
        messages.success(request, 'Groupe supprime.')
    return redirect('administration:groupes')


# ---------- Campagnes ----------

@admin_requis
def campagnes_liste(request):
    campagnes = (
        CampagneEvaluation.objects
        .select_related('enseignant', 'module', 'groupe')
        .annotate(
            nb_reponses=Count('reponses', distinct=True),
            nb_autorises=Count('evaluateurs_autorises', distinct=True),
        )
    )
    return render(request, 'administration/campagnes_liste.html', {
        'campagnes': campagnes,
    })


@admin_requis
def campagne_editer(request, pk=None):
    instance = get_object_or_404(CampagneEvaluation, pk=pk) if pk else None
    if request.method == 'POST':
        form = CampagneForm(request.POST, instance=instance)
        if form.is_valid():
            campagne = form.save()
            if instance is None:
                if form.cleaned_data.get('suggere_ia'):
                    suggestions = suggerer_evaluation(campagne.titre)
                    if suggestions:
                        for ordre, item in enumerate(suggestions, start=1):
                            QuestionEvaluation.objects.create(
                                campagne=campagne,
                                texte=item['texte'],
                                type_question=item['type'],
                                ordre=ordre,
                            )
                        messages.info(request, 'Questions proposees par l IA a partir du titre.')
                    else:
                        creer_questions_defaut(campagne)
                        messages.warning(
                            request,
                            "L IA n'a pas repondu : criteres par defaut appliques.",
                        )
                else:
                    creer_questions_defaut(campagne)
            messages.success(request, 'Campagne enregistree.')
            return redirect('administration:campagne_detail', pk=campagne.pk)
    else:
        form = CampagneForm(instance=instance)
    return render(request, 'administration/campagne_form.html', {
        'form': form,
        'campagne': instance,
    })


@admin_requis
def campagne_detail(request, pk):
    campagne = get_object_or_404(
        CampagneEvaluation.objects.select_related('enseignant', 'module', 'groupe'),
        pk=pk,
    )
    questions = campagne.questions.all()
    nb_autorises = campagne.evaluateurs_autorises.count()
    nb_reponses = campagne.reponses.count()
    stats = list(
        ReponseQuestionEvaluation.objects
        .filter(reponse__campagne=campagne, note__isnull=False)
        .values('question__texte', 'question_id')
        .annotate(moyenne=Avg('note'), total=Count('id'))
        .order_by('question_id')
    )
    commentaires = (
        ReponseQuestionEvaluation.objects
        .filter(reponse__campagne=campagne, reponse_texte__gt='')
        .select_related('question')
        .order_by('question__ordre')
    )
    if request.method == 'POST' and 'ajouter_question' in request.POST:
        qform = QuestionEvaluationForm(request.POST)
        if qform.is_valid():
            question = qform.save(commit=False)
            question.campagne = campagne
            question.save()
            messages.success(request, 'Question ajoutee.')
            return redirect('administration:campagne_detail', pk=pk)
    else:
        qform = QuestionEvaluationForm(initial={'ordre': questions.count() + 1})
    return render(request, 'administration/campagne_detail.html', {
        'campagne': campagne,
        'questions': questions,
        'nb_autorises': nb_autorises,
        'nb_reponses': nb_reponses,
        'stats': stats,
        'commentaires': commentaires,
        'qform': qform,
        'statuts': CampagneEvaluation.Statut.choices,
    })


@admin_requis
def campagne_statut(request, pk, statut):
    campagne = get_object_or_404(CampagneEvaluation, pk=pk)
    autorises = {c[0] for c in CampagneEvaluation.Statut.choices}
    if statut not in autorises:
        messages.error(request, 'Statut inconnu.')
        return redirect('administration:campagne_detail', pk=pk)
    if request.method == 'POST':
        campagne.statut = statut
        if statut == CampagneEvaluation.Statut.ACTIVE and not campagne.date_debut:
            campagne.date_debut = timezone.now()
        campagne.save(update_fields=['statut', 'date_debut'])
        messages.success(request, f'Campagne passee en « {campagne.get_statut_display()} ».')
    return redirect('administration:campagne_detail', pk=pk)


@admin_requis
def campagne_supprimer(request, pk):
    campagne = get_object_or_404(CampagneEvaluation, pk=pk)
    if campagne.reponses.exists():
        messages.error(
            request,
            'Impossible de supprimer une campagne qui a deja des reponses. Fermez-la.',
        )
        return redirect('administration:campagne_detail', pk=pk)
    if request.method == 'POST':
        campagne.delete()
        messages.success(request, 'Campagne supprimee.')
        return redirect('administration:campagnes')
    return render(request, 'administration/confirm_delete.html', {
        'objet': campagne,
        'titre': 'Supprimer la campagne',
        'retour': 'administration:campagnes',
    })


@admin_requis
def campagne_emails(request, pk):
    campagne = get_object_or_404(CampagneEvaluation, pk=pk)
    nb_avant = campagne.evaluateurs_autorises.count()
    if request.method == 'POST':
        form = AffectationClasseForm(request.POST)
        if form.is_valid():
            emails, ignores = form.emails_normalises()
            if not emails:
                messages.error(
                    request,
                    'Aucun etudiant ENSI pour cette classe ou filiere.',
                )
            else:
                ajoutes = 0
                for email in emails:
                    _, created = EvaluateurAutorise.objects.get_or_create(
                        campagne=campagne,
                        identifiant_anonyme=empreinte_email(email),
                    )
                    if created:
                        ajoutes += 1
                if ignores:
                    messages.warning(
                        request,
                        f'{len(ignores)} adresse(s) ignoree(s).',
                    )
                messages.success(
                    request,
                    f'{ajoutes} etudiant(s) de la classe / filiere autorise(s). '
                    'Les emails ne sont pas conserves en clair.',
                )
                return redirect('administration:campagne_detail', pk=pk)
    else:
        form = AffectationClasseForm()
    return render(request, 'administration/campagne_emails.html', {
        'campagne': campagne,
        'form': form,
        'nb_autorises': nb_avant,
    })


@admin_requis
def question_eval_supprimer(request, pk):
    question = get_object_or_404(QuestionEvaluation, pk=pk)
    campagne_id = question.campagne_id
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question supprimee.')
    return redirect('administration:campagne_detail', pk=campagne_id)


# ---------- Candidats ----------

@admin_requis
def candidats_liste(request):
    candidats = (
        ProfilCandidat.objects
        .select_related('utilisateur')
        .annotate(
            nb_tentatives=Count('tentatives'),
            nb_rdv=Count('rendez_vous'),
        )
        .order_by('-utilisateur__date_creation')
    )
    return render(request, 'administration/candidats_liste.html', {
        'candidats': candidats,
    })


@admin_requis
def candidat_detail(request, pk):
    profil = get_object_or_404(
        ProfilCandidat.objects.select_related('utilisateur', 'academique'),
        pk=pk,
    )
    if request.method == 'POST':
        form = CandidatStatutForm(request.POST, utilisateur=profil.utilisateur)
        if form.is_valid():
            profil.utilisateur.is_active = form.cleaned_data['is_active']
            profil.utilisateur.save(update_fields=['is_active'])
            messages.success(request, 'Statut du compte mis a jour.')
            return redirect('administration:candidat_detail', pk=pk)
    else:
        form = CandidatStatutForm(utilisateur=profil.utilisateur)
    recommandation = profil.recommandations.prefetch_related('lignes__formation').first()
    return render(request, 'administration/candidat_detail.html', {
        'profil': profil,
        'academique': getattr(profil, 'academique', None),
        'form': form,
        'recommandation': recommandation,
        'tentatives': profil.tentatives.all()[:10],
        'rdvs': profil.rendez_vous.select_related('conseiller__utilisateur')[:10],
    })


# ---------- Questionnaires ----------

@admin_requis
def questionnaires_liste(request):
    questionnaires = Questionnaire.objects.annotate(nb_questions=Count('questions'))
    if request.method == 'POST':
        form = QuestionnaireForm(request.POST)
        if form.is_valid():
            questionnaire = form.save()
            if form.cleaned_data.get('suggere_ia'):
                suggestions = suggerer_questionnaire(
                    questionnaire.titre,
                    Formation.objects.filter(est_active=True),
                )
                if suggestions:
                    for ordre, item in enumerate(suggestions, start=1):
                        question = Question.objects.create(
                            questionnaire=questionnaire,
                            texte=item['texte'],
                            ordre=ordre,
                        )
                        for option_texte in item['options']:
                            OptionReponse.objects.create(
                                question=question, texte=option_texte
                            )
                    messages.info(
                        request,
                        'Questions et reponses proposees par l IA. Ajustez les ponderations.',
                    )
                else:
                    messages.warning(
                        request,
                        "L IA n'a pas repondu. Ajoutez les questions manuellement.",
                    )
            messages.success(request, 'Questionnaire cree.')
            return redirect('administration:questionnaire_detail', pk=questionnaire.pk)
    else:
        form = QuestionnaireForm()
    return render(request, 'administration/questionnaires_liste.html', {
        'questionnaires': questionnaires,
        'form': form,
    })


@admin_requis
def questionnaire_detail(request, pk):
    questionnaire = get_object_or_404(Questionnaire, pk=pk)
    if request.method == 'POST':
        form = QuestionOrientationForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.questionnaire = questionnaire
            question.save()
            messages.success(request, 'Question ajoutee.')
            return redirect('administration:question_detail', pk=question.pk)
    else:
        form = QuestionOrientationForm(
            initial={'ordre': questionnaire.questions.count() + 1}
        )
    return render(request, 'administration/questionnaire_detail.html', {
        'questionnaire': questionnaire,
        'questions': questionnaire.questions.prefetch_related('options'),
        'form': form,
    })


@admin_requis
def question_detail(request, pk):
    question = get_object_or_404(Question, pk=pk)
    if request.method == 'POST' and 'sauver_question' in request.POST:
        form = QuestionOrientationForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            messages.success(request, 'Question mise a jour.')
            return redirect('administration:question_detail', pk=pk)
    else:
        form = QuestionOrientationForm(instance=question)
    if request.method == 'POST' and 'ajouter_option' in request.POST:
        oform = OptionReponseForm(request.POST)
        if oform.is_valid():
            option = oform.save(commit=False)
            option.question = question
            option.save()
            messages.success(request, 'Option ajoutee.')
            return redirect('administration:question_detail', pk=pk)
    else:
        oform = OptionReponseForm()
    return render(request, 'administration/question_detail.html', {
        'question': question,
        'form': form,
        'oform': oform,
        'options': question.options.prefetch_related('ponderations__formation'),
    })


@admin_requis
def question_supprimer(request, pk):
    question = get_object_or_404(Question, pk=pk)
    questionnaire_id = question.questionnaire_id
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question supprimee.')
    return redirect('administration:questionnaire_detail', pk=questionnaire_id)


@admin_requis
def option_ponderations(request, pk):
    option = get_object_or_404(OptionReponse.objects.select_related('question'), pk=pk)
    if request.method == 'POST':
        form = PonderationForm(request.POST)
        if form.is_valid():
            ponderation = form.save(commit=False)
            ponderation.option = option
            if PonderationOptionFormation.objects.filter(
                option=option, formation=ponderation.formation
            ).exists():
                messages.error(request, 'Cette ponderation existe deja.')
            else:
                ponderation.save()
                messages.success(request, 'Ponderation ajoutee.')
            return redirect('administration:option_ponderations', pk=pk)
    else:
        form = PonderationForm()
    return render(request, 'administration/option_ponderations.html', {
        'option': option,
        'form': form,
        'ponderations': option.ponderations.select_related('formation'),
    })


@admin_requis
def option_supprimer(request, pk):
    option = get_object_or_404(OptionReponse, pk=pk)
    question_id = option.question_id
    if request.method == 'POST':
        option.delete()
        messages.success(request, 'Option supprimee.')
    return redirect('administration:question_detail', pk=question_id)


@admin_requis
def ponderation_supprimer(request, pk):
    ponderation = get_object_or_404(PonderationOptionFormation, pk=pk)
    option_id = ponderation.option_id
    if request.method == 'POST':
        ponderation.delete()
        messages.success(request, 'Ponderation supprimee.')
    return redirect('administration:option_ponderations', pk=option_id)


# ---------- Conseillers / RDV ----------

@admin_requis
def conseillers_liste(request):
    conseillers = ProfilConseiller.objects.select_related('utilisateur').annotate(
        nb_rdv=Count('rendez_vous')
    )
    return render(request, 'administration/conseillers_liste.html', {
        'conseillers': conseillers,
    })


@admin_requis
def conseiller_editer(request, pk=None):
    instance = get_object_or_404(ProfilConseiller, pk=pk) if pk else None
    if request.method == 'POST':
        form = ConseillerForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Conseiller enregistre.')
            return redirect('administration:conseillers')
    else:
        form = ConseillerForm(instance=instance)
    return render(request, 'administration/conseiller_form.html', {
        'form': form,
        'conseiller': instance,
    })


@admin_requis
def rdv_liste(request):
    rdvs = (
        RendezVous.objects
        .select_related('candidat__utilisateur', 'conseiller__utilisateur')
        .order_by('-date_rendez_vous')
    )
    return render(request, 'administration/rdv_liste.html', {'rdvs': rdvs})


@admin_requis
def rdv_annuler(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)
    if request.method == 'POST':
        rdv.statut = RendezVous.Statut.ANNULE
        rdv.save(update_fields=['statut'])
        if rdv.disponibilite_id:
            rdv.disponibilite = None
            rdv.save(update_fields=['disponibilite'])
        messages.success(request, 'Rendez-vous annule.')
    return redirect('administration:rdv')


@admin_requis
def etudiants_liste(request):
    if request.method == 'POST':
        form = EtudiantInterneForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Etudiant ENSI enregistre.')
            return redirect('administration:etudiants')
    else:
        form = EtudiantInterneForm()
    return render(request, 'administration/etudiants_liste.html', {
        'etudiants': EtudiantInterne.objects.select_related('groupe'),
        'form': form,
    })


@admin_requis
def etudiant_supprimer(request, pk):
    etudiant = get_object_or_404(EtudiantInterne, pk=pk)
    if request.method == 'POST':
        etudiant.delete()
        messages.success(request, 'Etudiant retire de la base interne.')
    return redirect('administration:etudiants')


@admin_requis
def interets_liste(request):
    if request.method == 'POST':
        form = InteretForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Centre d'interet ajoute.")
            return redirect('administration:interets')
    else:
        form = InteretForm()
    return render(request, 'administration/interets_liste.html', {
        'interets': CentreInteret.objects.all(),
        'form': form,
    })


@admin_requis
def interet_supprimer(request, pk):
    interet = get_object_or_404(CentreInteret, pk=pk)
    if request.method == 'POST':
        interet.delete()
        messages.success(request, "Centre d'interet supprime.")
    return redirect('administration:interets')
