# GestionOrientation — ENSI Orientation

Plateforme web Django d'orientation academique et de suivi pedagogique :
dossier academique, questionnaire d'orientation, recommandations explicables,
rendez-vous conseillers et evaluation anonyme des enseignants.

## Demarrage

```bat
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe manage.py seed_demo
venv\Scripts\python.exe manage.py createsuperuser
venv\Scripts\python.exe manage.py runserver
```

## Comptes de demonstration

- **Conseiller** : `conseiller@ensi-uma.tn` / `conseiller123`
- **Evaluation anonyme** : emails autorises `etudiant1@ensi-uma.tn`, `etudiant2@ensi-uma.tn`, `etudiant3@ensi-uma.tn`

## Applications

| App | Role |
|-----|------|
| `accounts` | Utilisateur custom (email + role candidat/conseiller/admin) |
| `candidats` | Profil academique dynamique (Bac / Bac+2 / Bac+3), notes, interets |
| `formations` | Catalogue, prerequis, comparaison |
| `orientation` | Questionnaire, tentatives, moteur de recommandation (35/40/25) |
| `conseil` | Disponibilites, rendez-vous (creneau unique), espace conseiller |
| `evaluations` | Campagnes, liste blanche HMAC, reponses anonymes |
| `dashboard` | Tableaux de bord candidat et administrateur |

## Verification

```bat
venv\Scripts\python.exe smoke_test.py
```