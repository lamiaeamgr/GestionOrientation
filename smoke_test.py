"""Smoke test : verifie les flux principaux via le client de test Django.

Usage : venv\\Scripts\\python.exe smoke_test.py
"""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client  # noqa: E402

from accounts.models import Utilisateur  # noqa: E402
from evaluations.models import CampagneEvaluation, ReponseEvaluation  # noqa: E402
from orientation.models import TentativeQuestionnaire  # noqa: E402

c = Client()
resultats = []

# Nettoyage pour rendre le test rejouable
n, _ = Utilisateur.objects.filter(email__in=['candidat@test.tn']).delete()
r, _ = ReponseEvaluation.objects.all().delete()
print(f'[cleanup] {n} utilisateur(s), {r} reponse(s) evaluation supprimee(s)')


def check(nom, attendu, obtenu):
    ok = obtenu in (attendu if isinstance(attendu, (list, tuple)) else [attendu])
    resultats.append((nom, obtenu, ok))
    print(('OK  ' if ok else 'FAIL') + f' {nom}: {obtenu} (attendu {attendu})')


# --- Pages publiques ---
check('GET /', 200, c.get('/').status_code)
check('GET /formations/', 200, c.get('/formations/').status_code)
check('GET /evaluation/', 200, c.get('/evaluation/').status_code)
check('GET /comptes/connexion/', 200, c.get('/comptes/connexion/').status_code)
check('GET /comptes/inscription/', 200, c.get('/comptes/inscription/').status_code)

# --- Inscription candidat ---
resp = c.post('/comptes/inscription/', {
    'first_name': 'Test', 'last_name': 'Candidat',
    'email': 'candidat@test.tn',
    'password1': 'MotDePasse123!', 'password2': 'MotDePasse123!',
})
check('POST inscription', 302, resp.status_code)
if resp.status_code != 302:
    ctx = getattr(resp, 'context', None)
    form = ctx.get('form') if ctx else None
    print('    -> erreurs:', dict(form.errors) if form else resp.content[:400])
    print('    -> user cree:', Utilisateur.objects.filter(email='candidat@test.tn').exists())

# --- Dossier academique ---
check('GET profil', 200, c.get('/candidat/profil/').status_code)
resp = c.post('/candidat/profil/', {
    'objectif': 'public',
    'niveau_entree': 'bac', 'ville': 'Tanger', 'date_naissance': '2005-01-01',
    'type_diplome': 'sma', 'specialite': '', 'etablissement': 'Lycee Pilote',
    'ville_etablissement': 'Tanger', 'annee_obtention': 2026,
    'moyenne_generale': '16.5',
    'notes-TOTAL_FORMS': 3, 'notes-INITIAL_FORMS': 0,
    'notes-MIN_NUM_FORMS': 0, 'notes-MAX_NUM_FORMS': 1000,
    'notes-0-matiere': 1, 'notes-0-note': '17',
    'notes-1-matiere': 2, 'notes-1-note': '15',
    'notes-2-matiere': 3, 'notes-2-note': '18',
})
check('POST profil', 302, resp.status_code)

# --- Interets ---
resp = c.post('/candidat/interets/', {'domaines': [1, 2], 'activites': [13]})
check('POST interets', 302, resp.status_code)

# --- Questionnaire ---
resp = c.get('/orientation/demarrer/')
check('GET demarrer', 302, resp.status_code)
tentative = TentativeQuestionnaire.objects.latest('id')
check('GET tentative', 200, c.get(f'/orientation/tentative/{tentative.id}/').status_code)

post_data = {}
for q in tentative.questionnaire.questions.prefetch_related('options'):
    post_data[f'question_{q.id}'] = str(q.options.first().id)
resp = c.post(f'/orientation/tentative/{tentative.id}/', post_data)
check('POST tentative', 302, resp.status_code)
reco = tentative.recommandation
resp = c.get(f'/orientation/resultats/{reco.id}/')
check('GET resultats', 200, resp.status_code)
top = reco.lignes.first()
print(f'    -> Top recommandation : {top.formation.nom} ({top.score_final}%)')

# --- Rendez-vous ---
check('GET conseillers', 200, c.get('/conseil/conseillers/').status_code)
check('GET mes rdv', 200, c.get('/conseil/mes-rendez-vous/').status_code)

# --- Dashboard candidat ---
check('GET dashboard candidat', 200, c.get('/tableau-de-bord/candidat/').status_code)

# --- Evaluation anonyme ---
campagne = CampagneEvaluation.objects.filter(statut='active').first()
check('GET verifier', 200, c.get(f'/evaluation/{campagne.id}/').status_code)
resp = c.post(f'/evaluation/{campagne.id}/', {'email': 'etudiant1@ensi-uma.tn'})
check('POST verifier (autorise)', 302, resp.status_code)
resp = c.post(f'/evaluation/{campagne.id}/', {'email': 'inconnu@ensi-uma.tn'})
check('POST verifier (refuse)', 200, resp.status_code)

# Re-soumission eligibilite puis reponse
c.post(f'/evaluation/{campagne.id}/', {'email': 'etudiant1@ensi-uma.tn'})
post_eval = {}
for q in campagne.questions.all():
    post_eval[f'question_{q.id}'] = '4' if q.type_question == 'note' else 'Tres bien'
resp = c.post(f'/evaluation/{campagne.id}/repondre/', post_eval)
check('POST evaluation anonyme', 200, resp.status_code)

# Double soumission refusee
c.post(f'/evaluation/{campagne.id}/', {'email': 'etudiant1@ensi-uma.tn'})
resp = c.post(f'/evaluation/{campagne.id}/', {'email': 'etudiant1@ensi-uma.tn'})
check('Double soumission refusee', 200, resp.status_code)

# --- Conseiller ---
c2 = Client()
c2.post('/comptes/connexion-conseiller/', {
    'username': 'conseiller@ensi-uma.tn', 'password': 'ConseillerENSI2026',
})
check('GET espace conseiller', 200, c2.get('/espace-conseiller/').status_code)
check('GET disponibilites', 200, c2.get('/espace-conseiller/disponibilites/').status_code)

# --- Admin ---
c3 = Client()
c3.post('/comptes/connexion-admin/', {
    'username': 'admin@ensi.ma', 'password': 'AdminENSI2026',
})
check('GET administration', 200, c3.get('/administration/').status_code)
check('GET admin formations', 200, c3.get('/administration/formations/').status_code)
check('GET admin campagnes', 200, c3.get('/administration/evaluations/').status_code)
check('GET /admin/ masque', 404, c3.get('/admin/').status_code)

echecs = [r for r in resultats if not r[2]]
print(f'\n{len(resultats) - len(echecs)}/{len(resultats)} tests OK')
if echecs:
    raise SystemExit(1)
