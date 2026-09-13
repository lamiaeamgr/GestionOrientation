"""Conseiller IA via Groq : avis et questionnaire adapte au profil."""

import json
import logging
import re

from django.conf import settings

from candidats.catalogues import specialites_pour, types_pour

logger = logging.getLogger(__name__)

MODELES_GROQ = (
    'openai/gpt-oss-20b',
    'qwen/qwen3.8-27b',
    'groq/compound',
    'openai/gpt-oss-120b',
)


def _client_groq():
    cle = getattr(settings, 'GROQ_API_KEY', '') or ''
    if not cle:
        return None
    try:
        from groq import Groq
        return Groq(api_key=cle)
    except Exception:
        logger.exception('Impossible d\'initialiser Groq')
        return None


def _completer(client, messages, max_tokens=500, temperature=0.4):
    for modele in MODELES_GROQ:
        try:
            reponse = client.chat.completions.create(
                model=modele,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return (reponse.choices[0].message.content or '').strip()
        except Exception as exc:
            logger.warning('Groq modele %s indisponible: %s', modele, exc)
    return ''


def _libelle_filiere(profil, acad):
    if not acad or not acad.type_diplome:
        return ''
    for code, label in types_pour(profil.niveau_entree):
        if code == acad.type_diplome:
            return label
    return acad.type_diplome


def _libelle_specialite(profil, acad):
    if not acad or not acad.specialite:
        return ''
    for code, label in specialites_pour(profil.niveau_entree, acad.type_diplome):
        if code == acad.specialite:
            return label
    return acad.specialite


def _note_sur_20(valeur):
    if valeur in (None, ''):
        return 'non renseignee'
    return f'{valeur}/20'


def resume_profil(profil):
    acad = getattr(profil, 'academique', None)
    notes = []
    if acad:
        notes = [
            f'{n.matiere.nom} {_note_sur_20(n.note)}'
            for n in acad.notes.select_related('matiere')[:12]
        ]
    interets = [ic.interet.nom for ic in profil.interets.select_related('interet')]
    return {
        'niveau': profil.get_niveau_entree_display() if profil.niveau_entree else '',
        'objectif': profil.get_objectif_display() if profil.objectif else '',
        'filiere': _libelle_filiere(profil, acad),
        'specialite': _libelle_specialite(profil, acad),
        'moyenne': _note_sur_20(getattr(acad, 'moyenne_generale', None) if acad else None),
        'notes': notes,
        'interets': interets,
        'etablissement': getattr(acad, 'etablissement', '') or '',
    }


def _bloc_profil(resume):
    return (
        f"niveau={resume['niveau']}, projet={resume['objectif']}, "
        f"filiere={resume['filiere'] or 'n/a'}, specialite={resume['specialite'] or 'n/a'}, "
        f"etablissement={resume['etablissement'] or 'n/a'}, "
        f"moyenne generale={resume['moyenne']} (echelle 0 a 20, JAMAIS un pourcentage), "
        f"notes=[{', '.join(resume['notes']) or 'n/a'}], "
        f"interets={', '.join(resume['interets']) or 'n/a'}."
    )


def generer_avis_ia(profil, lignes):
    """Retourne un texte court, ou une chaine vide si Groq est indisponible."""
    client = _client_groq()
    if client is None:
        return ''

    top = list(lignes[:5])
    resume = resume_profil(profil)
    classement = '\n'.join(
        f'- {l.formation.nom} ({l.formation.get_reconnaissance_display()}) : score d\'adequation {l.score_final}/100'
        for l in top
    )
    prompt = (
        "Tu es conseiller d'orientation a l'ENSI (Tanger). "
        "Reponds en francais, 3 a 5 phrases, ton professionnel. "
        "REGLE ABSOLUE : les moyennes et notes sont sur 20 "
        "(exemple : 17,56/20). N'ecris JAMAIS une moyenne suivie de %. "
        "Le % n'est autorise que pour le score d'adequation d'une formation (score /100). "
        "N'invente aucune formation hors de la liste.\n\n"
        f"Candidat : {_bloc_profil(resume)}\n"
        f"Classement (score /100) :\n{classement}\n"
        "Explique le meilleur choix en citant la moyenne /20 et un conseil concret."
    )
    return _completer(
        client,
        [
            {
                'role': 'system',
                'content': (
                    "Conseiller d'orientation ENSI. Notes scolaires toujours /20. "
                    "Jamais de moyenne en pourcentage."
                ),
            },
            {'role': 'user', 'content': prompt},
        ],
        max_tokens=400,
    )


def _extraire_json(texte):
    if not texte:
        return None
    texte = texte.strip()
    bloc = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', texte, flags=re.S)
    if bloc:
        texte = bloc.group(1)
    try:
        return json.loads(texte)
    except json.JSONDecodeError:
        debut, fin = texte.find('{'), texte.rfind('}')
        if debut >= 0 and fin > debut:
            try:
                return json.loads(texte[debut:fin + 1])
            except json.JSONDecodeError:
                return None
    return None


def generer_questionnaire_personnalise(profil, questions):
    """Reecrit les questions/options selon le dossier. Conserve les IDs."""
    client = _client_groq()
    if client is None or not questions:
        return {}

    resume = resume_profil(profil)
    payload = []
    for question in questions:
        payload.append({
            'id': question.id,
            'texte': question.texte,
            'options': [
                {'id': opt.id, 'texte': opt.texte}
                for opt in question.options.all()
            ],
        })

    prompt = (
        "Adapte ce questionnaire d'orientation au profil du candidat. "
        "Reformule chaque question et chaque option pour qu'elles parlent "
        "de SON parcours (filiere, specialite, notes /20, projet). "
        "Garde EXACTEMENT les memes id. Ne change pas le nombre d'options. "
        "Ne parle jamais d'une moyenne en pourcentage : c'est /20. "
        "Reponds UNIQUEMENT en JSON : "
        '{"intro":"...", "questions":{"<id>":{"texte":"...","options":{"<id>":"..."}}}}\n\n'
        f"Profil : {_bloc_profil(resume)}\n"
        f"Questionnaire : {json.dumps(payload, ensure_ascii=False)}"
    )
    brut = _completer(
        client,
        [
            {
                'role': 'system',
                'content': (
                    "Tu personnalises un questionnaire d'orientation. "
                    "JSON strict, IDs inchanges, notes toujours /20."
                ),
            },
            {'role': 'user', 'content': prompt},
        ],
        max_tokens=1800,
        temperature=0.5,
    )
    data = _extraire_json(brut)
    if not isinstance(data, dict) or 'questions' not in data:
        return {}
    return data


def _extraire_liste(texte):
    data = _extraire_json(texte)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for cle in ('questions', 'criteres', 'items'):
            if isinstance(data.get(cle), list):
                return data[cle]
    if not texte:
        return None
    debut, fin = texte.find('['), texte.rfind(']')
    if debut >= 0 and fin > debut:
        try:
            data = json.loads(texte[debut:fin + 1])
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            return None
    return None


def suggerer_questionnaire(titre, formations=None):
    """Propose questions + options a partir du titre du questionnaire."""
    client = _client_groq()
    if client is None:
        return []
    noms = [f.nom for f in (formations or [])][:12]
    prompt = (
        "Tu crees un questionnaire d'orientation pour l'ENSI (Tanger). "
        "5 questions de mise en situation (pas trop directes), "
        "4 options chacune. Reponds UNIQUEMENT en JSON : "
        '[{"texte":"...","options":["...","...","...","..."]}]\n\n'
        f"Titre : {titre}\n"
        f"Formations possibles : {', '.join(noms) or 'Genie Informatique, Civil, Industriel, Licence, Master'}."
    )
    brut = _completer(
        client,
        [
            {
                'role': 'system',
                'content': "JSON strict. Questions d'orientation ENSI, francais, sans accents dans les cles.",
            },
            {'role': 'user', 'content': prompt},
        ],
        max_tokens=1600,
        temperature=0.5,
    )
    items = _extraire_liste(brut) or []
    propres = []
    for item in items[:8]:
        if not isinstance(item, dict):
            continue
        texte = (item.get('texte') or '').strip()
        options = [str(o).strip() for o in (item.get('options') or []) if str(o).strip()]
        if texte and len(options) >= 2:
            propres.append({'texte': texte, 'options': options[:6]})
    return propres


def suggerer_evaluation(titre):
    """Propose les criteres d'une evaluation d'enseignant a partir du titre."""
    client = _client_groq()
    if client is None:
        return []
    prompt = (
        "Tu proposes les questions d'une evaluation anonyme d'enseignant a l'ENSI. "
        "7 criteres notes 1-5 et 2 commentaires libres (points positifs / a ameliorer). "
        "Reponds UNIQUEMENT en JSON : "
        '[{"texte":"...","type":"note"|"texte"}]\n\n'
        f"Titre de la campagne : {titre}"
    )
    brut = _completer(
        client,
        [
            {
                'role': 'system',
                'content': "JSON strict. Evaluation pedagogique, francais.",
            },
            {'role': 'user', 'content': prompt},
        ],
        max_tokens=900,
        temperature=0.3,
    )
    items = _extraire_liste(brut) or []
    propres = []
    for item in items[:12]:
        if not isinstance(item, dict):
            continue
        texte = (item.get('texte') or '').strip()
        type_q = (item.get('type') or 'note').strip().lower()
        if type_q not in ('note', 'texte'):
            type_q = 'note'
        if texte:
            propres.append({'texte': texte, 'type': type_q})
    return propres


def appliquer_personnalisation(questions, perso):
    """Ecrit les textes IA sur les objets question/option (affichage uniquement)."""
    if not perso:
        return questions, ''
    mapping = perso.get('questions') or {}
    for question in questions:
        bloc = mapping.get(str(question.id)) or mapping.get(question.id)
        if not bloc:
            continue
        if bloc.get('texte'):
            question.texte = bloc['texte']
        options = bloc.get('options') or {}
        for option in question.options.all():
            texte = options.get(str(option.id)) or options.get(option.id)
            if texte:
                option.texte = texte
    return questions, perso.get('intro') or ''
