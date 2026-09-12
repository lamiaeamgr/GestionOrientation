from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import DisponibiliteForm, NoteConseillerForm, ReservationForm
from .models import DisponibiliteConseiller, ProfilConseiller, RendezVous


# ---------- Espace candidat ----------

@login_required
def liste_conseillers(request):
    """Liste des conseillers et de leurs creneaux reservables."""
    if not request.user.est_candidat:
        messages.error(request, "Cette page est reservee aux candidats.")
        return redirect('dashboard:home')
    conseillers = ProfilConseiller.objects.select_related('utilisateur').prefetch_related(
        'disponibilites'
    )
    donnees = []
    for conseiller in conseillers:
        creneaux = [
            d for d in conseiller.disponibilites.all() if d.est_reservable
        ]
        donnees.append({'conseiller': conseiller, 'creneaux': creneaux})
    return render(request, 'conseil/conseillers.html', {'donnees': donnees})


@login_required
def reserver(request, disponibilite_id):
    """Reservation d'un creneau : un creneau ne peut etre pris qu'une fois."""
    if not request.user.est_candidat:
        messages.error(request, "Cette page est reservee aux candidats.")
        return redirect('dashboard:home')
    profil = request.user.profil_candidat
    dispo = get_object_or_404(
        DisponibiliteConseiller.objects.select_related('conseiller__utilisateur'),
        pk=disponibilite_id,
    )
    if not dispo.est_reservable:
        messages.error(request, "Ce creneau n'est plus disponible.")
        return redirect('conseil:conseillers')

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    rdv = form.save(commit=False)
                    rdv.candidat = profil
                    rdv.conseiller = dispo.conseiller
                    rdv.disponibilite = dispo
                    rdv.date_rendez_vous = dispo.date_heure_debut
                    rdv.save()
            except IntegrityError:
                messages.error(request, 'Ce creneau vient d etre reserve par un autre candidat.')
                return redirect('conseil:conseillers')
            messages.success(request, 'Votre rendez-vous est confirme.')
            return redirect('conseil:mes_rdv')
    else:
        form = ReservationForm()
    return render(request, 'conseil/reserver.html', {'dispo': dispo, 'form': form})


@login_required
def mes_rdv(request):
    if not request.user.est_candidat:
        messages.error(request, "Cette page est reservee aux candidats.")
        return redirect('dashboard:home')
    rdvs = (
        request.user.profil_candidat.rendez_vous
        .select_related('conseiller__utilisateur')
    )
    a_venir = rdvs.filter(
        statut=RendezVous.Statut.CONFIRME, date_rendez_vous__gte=timezone.now()
    )
    passes = rdvs.exclude(pk__in=a_venir)
    return render(request, 'conseil/mes_rdv.html', {
        'a_venir': a_venir, 'passes': passes,
    })


@login_required
def annuler_rdv(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)
    est_proprietaire = (
        request.user.est_candidat
        and rdv.candidat.utilisateur_id == request.user.id
    )
    est_conseiller = (
        request.user.est_conseiller
        and rdv.conseiller.utilisateur_id == request.user.id
    )
    if not (est_proprietaire or est_conseiller or request.user.est_admin):
        messages.error(request, 'Acces non autorise.')
        return redirect('dashboard:home')
    if request.method == 'POST':
        rdv.statut = RendezVous.Statut.ANNULE
        rdv.save(update_fields=['statut'])
        # Le creneau redevient reservable
        if rdv.disponibilite_id:
            rdv.disponibilite = None
            rdv.save(update_fields=['disponibilite'])
        messages.success(request, 'Le rendez-vous a ete annule.')
    return redirect('conseil:mes_rdv' if est_proprietaire else 'conseil:espace')


# ---------- Espace conseiller ----------

def _conseiller(request):
    if not request.user.est_conseiller:
        return None
    profil, _ = ProfilConseiller.objects.get_or_create(utilisateur=request.user)
    return profil


@login_required
def espace(request):
    conseiller = _conseiller(request)
    if conseiller is None:
        messages.error(request, "Cette page est reservee aux conseillers.")
        return redirect('dashboard:home')
    rdvs = conseiller.rendez_vous.select_related('candidat__utilisateur')
    a_venir = rdvs.filter(
        statut=RendezVous.Statut.CONFIRME, date_rendez_vous__gte=timezone.now()
    )
    passes = rdvs.exclude(pk__in=a_venir)
    return render(request, 'conseil/espace.html', {
        'conseiller': conseiller, 'a_venir': a_venir, 'passes': passes,
    })


@login_required
def disponibilites(request):
    conseiller = _conseiller(request)
    if conseiller is None:
        messages.error(request, "Cette page est reservee aux conseillers.")
        return redirect('dashboard:home')
    if request.method == 'POST':
        form = DisponibiliteForm(request.POST)
        if form.is_valid():
            dispo = form.save(commit=False)
            dispo.conseiller = conseiller
            dispo.save()
            messages.success(request, 'Creneau ajoute.')
            return redirect('conseil:disponibilites')
    else:
        form = DisponibiliteForm()
    creneaux = conseiller.disponibilites.select_related().all()
    return render(request, 'conseil/disponibilites.html', {
        'form': form, 'creneaux': creneaux,
    })


@login_required
def supprimer_disponibilite(request, pk):
    conseiller = _conseiller(request)
    if conseiller is None:
        messages.error(request, "Cette page est reservee aux conseillers.")
        return redirect('dashboard:home')
    dispo = get_object_or_404(DisponibiliteConseiller, pk=pk, conseiller=conseiller)
    if request.method == 'POST':
        if hasattr(dispo, 'rendez_vous'):
            messages.error(request, 'Impossible : ce creneau est deja reserve.')
        else:
            dispo.delete()
            messages.success(request, 'Creneau supprime.')
    return redirect('conseil:disponibilites')


@login_required
def rdv_detail(request, pk):
    """Fiche rendez-vous cote conseiller : dossier candidat + note."""
    conseiller = _conseiller(request)
    if conseiller is None:
        messages.error(request, "Cette page est reservee aux conseillers.")
        return redirect('dashboard:home')
    rdv = get_object_or_404(
        RendezVous.objects.select_related('candidat__utilisateur'),
        pk=pk, conseiller=conseiller,
    )
    if request.method == 'POST':
        form = NoteConseillerForm(request.POST, instance=rdv)
        if form.is_valid():
            form.save()
            messages.success(request, 'Note enregistree.')
            return redirect('conseil:espace')
    else:
        form = NoteConseillerForm(instance=rdv)
    profil_cand = rdv.candidat
    academique = getattr(profil_cand, 'academique', None)
    recommandation = profil_cand.recommandations.prefetch_related(
        'lignes__formation'
    ).first()
    return render(request, 'conseil/rdv_detail.html', {
        'rdv': rdv,
        'form': form,
        'profil': profil_cand,
        'academique': academique,
        'recommandation': recommandation,
    })
