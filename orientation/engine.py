"""Moteur de recommandation deterministe et explicable.

Score final = 35 % academique + 40 % questionnaire + 25 % centres d'interet
(ponderations configurables dans settings).
"""
from decimal import Decimal

from django.conf import settings

from candidats.models import CentreInteret
from formations.models import Formation

from .models import (
    PonderationOptionFormation,
    Recommandation,
    RecommandationFormation,
)

# Correspondance indicative entre centres d'interet et mots-cles de domaine.
# Les correspondances exactes sont enrichies par les matieres importantes
# et les ponderations definies en base.
MOTS_CLES_INTERETS = {
    'Programmation': ['informatique', 'web', 'mobile', 'logiciel'],
    'Intelligence artificielle': ['informatique', 'data', 'ia', 'big data'],
    'Cybersecurite': ['informatique', 'cybersecurite', 'reseaux'],
    'Analyse de donnees': ['informatique', 'data', 'big data', 'statistique'],
    'Mathematiques': ['informatique', 'industriel', 'prepa'],
    'Construction': ['civil', 'batiment', 'construction'],
    'Systemes industriels': ['industriel', 'production', 'mecanique'],
    'Finance': ['finance', 'gestion', 'economie'],
    'Marketing': ['marketing', 'commerce', 'communication'],
    'Logistique': ['industriel', 'logistique', 'transport'],
    'Management': ['industriel', 'management', 'gestion'],
    'Reseaux': ['informatique', 'reseaux', 'telecom'],
}

MOTS_CLES_ACTIVITES = {
    'Resoudre des problemes': ['informatique', 'industriel', 'ingenieur'],
    'Concevoir': ['civil', 'informatique', 'industriel'],
    'Programmer': ['informatique', 'web', 'mobile'],
    'Analyser': ['informatique', 'data', 'industriel'],
    'Travailler avec des chiffres': ['informatique', 'finance', 'industriel'],
    'Organiser': ['industriel', 'civil', 'management'],
    'Communiquer': ['marketing', 'management'],
    'Gerer une equipe': ['industriel', 'management', 'civil'],
}


def _texte_formation(formation):
    morceaux = [formation.nom, formation.domaine, formation.parcours or '']
    if formation.parent:
        morceaux += [formation.parent.nom, formation.parent.domaine]
    return ' '.join(morceaux).lower()


def score_academique(profil, formation):
    """Score /100 base sur la moyenne generale et les prerequis par matiere."""
    academique = getattr(profil, 'academique', None)
    if academique is None:
        return Decimal('0'), ['Dossier academique non renseigne.']

    details = []
    notes = {n.matiere_id: n.note for n in academique.notes.select_related('matiere')}
    matieres = {n.matiere_id: n.matiere.nom for n in academique.notes.select_related('matiere')}

    # 1) Moyenne generale -> base sur 100
    base = Decimal('0')
    if academique.moyenne_generale is not None:
        base = Decimal(academique.moyenne_generale) * 5
        details.append(
            f"Moyenne generale {academique.moyenne_generale}/20 -> {base:.0f} points de base."
        )
    else:
        moyennes = [
            m for m in (
                academique.moyenne_annee_1,
                academique.moyenne_annee_2,
                academique.moyenne_annee_3,
            ) if m is not None
        ]
        if moyennes:
            moy = sum(moyennes) / len(moyennes)
            base = Decimal(moy) * 5
            details.append(f'Moyenne des annees {moy:.2f}/20 -> {base:.0f} points de base.')

    # 2) Adequation aux prerequis de la formation
    prerequis = list(formation.prerequis.select_related('matiere'))
    bonus = Decimal('0')
    if prerequis:
        poids_total = sum(p.poids for p in prerequis) or 1
        acquis = Decimal('0')
        for p in prerequis:
            note = notes.get(p.matiere_id)
            if note is None:
                continue
            ratio = min(Decimal(note) / Decimal(p.note_minimale), Decimal('1.25'))
            acquis += Decimal(p.poids) * ratio
            if note >= p.note_minimale:
                details.append(
                    f'{p.matiere.nom} : {note}/20 >= prerequis {p.note_minimale}/20.'
                )
            else:
                details.append(
                    f'{p.matiere.nom} : {note}/20 < prerequis {p.note_minimale}/20.'
                )
        bonus = (acquis / poids_total) * Decimal('40')
    else:
        # Pas de prerequis declares : on valorise les matieres importantes
        importantes = {m.id for m in formation.matieres_importantes.all()}
        notes_importantes = [notes[mid] for mid in importantes if mid in notes]
        if notes_importantes:
            moy = sum(notes_importantes) / len(notes_importantes)
            bonus = Decimal(moy) * 2
            noms = [matieres[mid] for mid in importantes if mid in notes]
            details.append(
                f"Bonnes notes dans les matieres cles ({', '.join(noms)})."
            )

    score = min(base * Decimal('0.6') + bonus, Decimal('100'))
    return score.quantize(Decimal('0.01')), details


def score_interets(profil, formation):
    """Score /100 selon la correspondance interets <-> domaine de la formation."""
    interets = [
        ic.interet for ic in profil.interets.select_related('interet')
    ]
    if not interets:
        return Decimal('0'), ["Aucun centre d'interet renseigne."]

    texte = _texte_formation(formation)
    details = []
    nb_match = 0
    for interet in interets:
        mots = MOTS_CLES_INTERETS.get(interet.nom) or MOTS_CLES_ACTIVITES.get(interet.nom) or []
        if any(m in texte for m in mots) or interet.nom.lower() in texte:
            nb_match += 1
            details.append(f"Interet '{interet.nom}' coherent avec la formation.")
    score = Decimal(nb_match) / Decimal(len(interets)) * 100
    return score.quantize(Decimal('0.01')), details


def score_questionnaire(tentative, formation):
    """Score /100 : somme des poids des options choisies pour cette formation,
    normalisee par le poids maximal atteignable."""
    options_ids = list(
        tentative.reponses.values_list('option_id', flat=True)
    )
    if not options_ids:
        return Decimal('0'), []

    ponderations = PonderationOptionFormation.objects.filter(
        option_id__in=options_ids
    ).select_related('option__question', 'formation')

    obtenu = sum(p.poids for p in ponderations if p.formation_id == formation.id)
    # Poids maximal theorique : meilleure option par question pour cette formation
    questions_ids = {p.option.question_id for p in ponderations}
    if not questions_ids:
        questions_ids = set(
            tentative.reponses.values_list('question_id', flat=True)
        )
    maximum = 0
    for qid in questions_ids:
        meilleur = (
            PonderationOptionFormation.objects
            .filter(option__question_id=qid, formation=formation)
            .order_by('-poids')
            .values_list('poids', flat=True)
            .first()
        )
        maximum += meilleur or 0

    details = [
        f"{p.option.question.texte[:60]} -> '{p.option.texte[:50]}' (+{p.poids})"
        for p in ponderations if p.formation_id == formation.id and p.poids > 0
    ]
    if maximum <= 0:
        return Decimal('0'), details
    score = Decimal(obtenu) / Decimal(maximum) * 100
    return min(score, Decimal('100')).quantize(Decimal('0.01')), details


def generer_recommandation(profil, tentative):
    """Calcule et enregistre le classement des formations pour une tentative."""
    poids_acad = Decimal(getattr(settings, 'POIDS_SCORE_ACADEMIQUE', 35)) / 100
    poids_quest = Decimal(getattr(settings, 'POIDS_SCORE_QUESTIONNAIRE', 40)) / 100
    poids_int = Decimal(getattr(settings, 'POIDS_SCORE_INTERETS', 25)) / 100

    recommandation = Recommandation.objects.create(profil=profil, tentative=tentative)

    formations = Formation.objects.filter(est_active=True).prefetch_related(
        'matieres_importantes', 'prerequis__matiere'
    )
    for formation in formations:
        s_acad, d_acad = score_academique(profil, formation)
        s_int, d_int = score_interets(profil, formation)
        s_quest, d_quest = score_questionnaire(tentative, formation)
        final = (s_acad * poids_acad + s_quest * poids_quest + s_int * poids_int)
        final = final.quantize(Decimal('0.01'))
        RecommandationFormation.objects.create(
            recommandation=recommandation,
            formation=formation,
            score_academique=s_acad,
            score_interets=s_int,
            score_questionnaire=s_quest,
            score_final=final,
            explication={
                'academique': d_acad,
                'interets': d_int,
                'questionnaire': d_quest,
            },
        )
    return recommandation
