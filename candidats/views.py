from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .catalogues import VILLES_MAROC
from .forms import InteretsForm, NotesFiliereForm, ProfilAcademiqueForm, ProfilCandidatForm
from .models import ProfilAcademique, ProfilCandidat


def _profil_candidat(request):
    """Retourne le profil candidat de l'utilisateur, en le creant si besoin."""
    if not request.user.est_candidat:
        return None
    profil, _ = ProfilCandidat.objects.get_or_create(utilisateur=request.user)
    return profil


def _contexte_academique(request, profil_cand, academique):
    if request.method == 'POST':
        source = request.POST
    elif any(k in request.GET for k in ('niveau_entree', 'type_diplome', 'specialite')):
        source = request.GET
    else:
        source = None
    niveau = (source.get('niveau_entree') if source else None) or profil_cand.niveau_entree
    type_diplome = (source.get('type_diplome') if source else None) or academique.type_diplome
    specialite = (source.get('specialite') if source else None) or academique.specialite
    return source, niveau, type_diplome, specialite


@login_required
def profil(request):
    """Dossier academique : filieres marocaines et matieres dynamiques."""
    profil_cand = _profil_candidat(request)
    if profil_cand is None:
        messages.error(request, "Cette page est reservee aux candidats.")
        return redirect('dashboard:home')

    academique, _ = ProfilAcademique.objects.get_or_create(profil=profil_cand)
    source, niveau, type_diplome, specialite = _contexte_academique(
        request, profil_cand, academique
    )

    if request.method == 'POST':
        form_profil = ProfilCandidatForm(request.POST, instance=profil_cand)
        form_acad = ProfilAcademiqueForm(
            request.POST, instance=academique, niveau=niveau, type_diplome=type_diplome
        )
        form_notes = NotesFiliereForm(
            request.POST,
            academique=academique,
            niveau=niveau,
            type_diplome=type_diplome,
            specialite=specialite,
        )
        if form_profil.is_valid() and form_acad.is_valid() and form_notes.is_valid():
            form_profil.save()
            form_acad.save()
            form_notes.save()
            profil_cand.profil_complete = True
            profil_cand.save(update_fields=['profil_complete'])
            messages.success(request, 'Votre dossier academique a ete enregistre.')
            return redirect('candidats:interets')
    else:
        form_profil = ProfilCandidatForm(source, instance=profil_cand)
        form_acad = ProfilAcademiqueForm(
            source, instance=academique, niveau=niveau, type_diplome=type_diplome
        )
        form_notes = NotesFiliereForm(
            academique=academique,
            niveau=niveau,
            type_diplome=type_diplome,
            specialite=specialite,
        )

    return render(request, 'candidats/profil.html', {
        'form_profil': form_profil,
        'form_acad': form_acad,
        'form_notes': form_notes,
        'profil': profil_cand,
        'villes': VILLES_MAROC,
    })


@login_required
def interets(request):
    profil_cand = _profil_candidat(request)
    if profil_cand is None:
        messages.error(request, "Cette page est reservee aux candidats.")
        return redirect('dashboard:home')

    if request.method == 'POST':
        form = InteretsForm(request.POST, profil=profil_cand)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos centres d'interet ont ete enregistres.")
            return redirect('dashboard:home')
    else:
        form = InteretsForm(profil=profil_cand)
    return render(request, 'candidats/interets.html', {'form': form})


@login_required
def detail_profil(request, pk):
    """Consultation du dossier d'un candidat (conseiller / admin)."""
    if not (request.user.est_conseiller or request.user.est_admin):
        messages.error(request, 'Acces non autorise.')
        return redirect('dashboard:home')
    profil_cand = get_object_or_404(
        ProfilCandidat.objects.select_related('utilisateur'), pk=pk
    )
    academique = getattr(profil_cand, 'academique', None)
    notes = academique.notes.select_related('matiere') if academique else []
    interets = profil_cand.interets.select_related('interet')
    recommandations = profil_cand.recommandations.prefetch_related('lignes__formation')
    return render(request, 'candidats/detail.html', {
        'profil': profil_cand,
        'academique': academique,
        'notes': notes,
        'interets': interets,
        'recommandations': recommandations,
    })
