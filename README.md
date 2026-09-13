# ENSI Orientation

Plateforme Django d'orientation academique et de suivi pedagogique pour
l'Ecole des Nouvelles Sciences et Ingenierie (ENSI Tanger).

Elle couvre trois espaces authentifies — **candidat**, **conseiller**,
**administrateur** — plus un parcours **public anonyme** pour l'evaluation
des enseignants.

## Fonctionnalites

- Inscription courte puis dossier academique dynamique (Bac / Bac+2 / Bac+3, filieres marocaines).
- Centres d'interet, questionnaire d'orientation personnalise (IA Groq si cle presente).
- Recommandations explicables (profil 35 % + questionnaire 40 % + interets 25 %).
- Filtrage selon le projet : secteur public (formations reconnues) ou prive (reconnues + accreditees).
- Comparaison de formations et prise de rendez-vous avec un conseiller.
- Evaluation anonyme des enseignants (liste blanche HMAC, une reponse par etudiant).
- Espace d'administration metier : formations, campagnes, questionnaires, comptes, statistiques.
- Sessions separees : les trois roles peuvent rester connectes en parallele dans le meme navigateur.

L'interface d'administration Django (`/admin/`) n'est **pas exposee**.

## Installation

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py seed_demo
venv\Scripts\python.exe manage.py runserver
```

Le fichier `.env` (ignore par Git) contient `SECRET_KEY`, `DEBUG`,
`ALLOWED_HOSTS`, `EVALUATION_HMAC_KEY` et optionnellement `GROQ_API_KEY`.

Application : http://127.0.0.1:8000/

## Comptes de demonstration

`seed_demo` cree les trois comptes. Chaque ecran de connexion les
**pre-remplit** : il suffit de cliquer sur « Se connecter ».

Les sessions sont isolees (cookies distincts). Ouvrez chaque role dans
un onglet : se deconnecter de l'un ne ferme pas les autres.

| Role | Page | Email | Mot de passe |
|------|------|-------|--------------|
| **Candidat** | http://127.0.0.1:8000/comptes/connexion/ | `candidat@ensi.ma` | `CandidatENSI2026` |
| **Conseiller** | http://127.0.0.1:8000/comptes/connexion-conseiller/ | `conseiller@ensi-uma.tn` | `ConseillerENSI2026` |
| **Admin** | http://127.0.0.1:8000/comptes/connexion-admin/ | `admin@ensi.ma` | `AdminENSI2026` |

Le candidat de demonstration (Yasmine Alaoui) a un dossier Bac SMA a Tanger
deja complete, avec interets numeriques.

**Evaluation anonyme** (sans compte) : http://127.0.0.1:8000/evaluation/  
Emails autorises sur la campagne de demo : `etudiant1@ensi-uma.tn`,
`etudiant2@ensi-uma.tn`, `etudiant3@ensi-uma.tn`.  
Ils sont stockes uniquement sous forme d'empreinte HMAC, jamais en clair.
Un email admin ou conseiller est refuse.

## Espaces et parcours

### Candidat

1. Inscription (prenom, nom, email, mot de passe) ou connexion demo.
2. Projet (public / prive) puis dossier academique selon le niveau.
3. Centres d'interet.
4. Questionnaire, resultats expliques, historique, comparaison.
5. Reservation d'un creneau conseiller.

### Conseiller

- Disponibilites, rendez-vous a venir.
- Consultation du dossier et des recommandations du candidat.
- Note / compte-rendu apres entretien.

### Administrateur (`/administration/`)

- Pilotage : candidats, profils completes, tests, RDV, stats d'orientation.
- CRUD formations et prerequis (actives / archivees, reconnue / accreditee).
- CRUD campagnes d'evaluation : enseignants, modules, groupes, questions, cycle de vie.
- Images de formations uploadables (catalogue candidat).
- Centres d'interet et etudiants internes ENSI geres depuis l'admin.
- Suggestions IA (Groq) a la creation d'un questionnaire ou d'une campagne.
- Liste blanche : affectation par classe / filiere (emails @ensi en empreinte HMAC).
  L'admin voit le nombre d'autorises et de reponses, **jamais qui a repondu**.
- Graphiques de pilotage (recommandations, niveaux, RDV, evaluations).
- Gestion des candidats (activation / suspension), questionnaires et ponderations.
- Conseillers et suivi des rendez-vous.

### Evaluation publique

Page sans authentification. L'etudiant saisit son email : eligibilite +
unicite via empreinte. Les reponses pedagogiques ne contiennent ni nom
ni email.

## Applications Django

| App | Role |
|-----|------|
| `accounts` | Utilisateur email + role, 3 connexions, sessions separees |
| `candidats` | Profil, notes /20, catalogues marocains, interets |
| `formations` | Catalogue public, comparaison |
| `orientation` | Questionnaire, moteur 35/40/25, avis IA |
| `conseil` | Creneaux uniques, RDV, espace conseiller |
| `evaluations` | Campagnes, HMAC, reponses anonymes |
| `administration` | Back-office metier (pas Django Admin) |
| `dashboard` | Accueil public et tableau de bord candidat |

## Identite visuelle

Charte alignee sur [ensit.ma](https://ensit.ma/) : bleu ENSI, accent rouge,
logo officiel, photos campus. Les pages de connexion n'affichent pas le
pied de page.

## Verification

```bat
venv\Scripts\python.exe smoke_test.py
```
