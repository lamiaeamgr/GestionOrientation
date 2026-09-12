"""Peuple la base avec des donnees de demonstration conformes au cadrage :
matieres, centres d'interet, formations, questionnaire, conseiller, campagne.

Usage : python manage.py seed_demo
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Utilisateur
from candidats.models import CentreInteret, Matiere
from conseil.models import DisponibiliteConseiller, ProfilConseiller
from evaluations.models import (
    CampagneEvaluation,
    Enseignant,
    EvaluateurAutorise,
    GroupeEtudiant,
    Module,
    QuestionEvaluation,
)
from evaluations.utils import empreinte_email
from formations.models import Formation, PrerequisFormation
from orientation.models import (
    OptionReponse,
    PonderationOptionFormation,
    Question,
    Questionnaire,
)


class Command(BaseCommand):
    help = 'Cree les donnees de demonstration de la plateforme ENSI Orientation.'

    def handle(self, *args, **options):
        self._matieres()
        self._interets()
        formations = self._formations()
        self._questionnaire(formations)
        self._conseiller()
        self._campagne()
        self.stdout.write(self.style.SUCCESS('Donnees de demonstration creees.'))

    # ------------------------------------------------------------------
    def _matieres(self):
        self.matieres = {}
        for nom in [
            'Mathematiques', 'Physique', 'Informatique', 'SVT',
            'Francais', 'Anglais', 'Sciences techniques', 'Economie',
            'Gestion', 'Algorithmique', 'Statistiques', 'Mecanique',
        ]:
            self.matieres[nom], _ = Matiere.objects.get_or_create(nom=nom)

    def _interets(self):
        domaines = [
            'Programmation', 'Intelligence artificielle', 'Cybersecurite',
            'Analyse de donnees', 'Mathematiques', 'Construction',
            'Systemes industriels', 'Finance', 'Marketing', 'Logistique',
            'Management', 'Reseaux',
        ]
        activites = [
            'Resoudre des problemes', 'Concevoir', 'Programmer', 'Analyser',
            'Travailler avec des chiffres', 'Organiser', 'Communiquer',
            'Gerer une equipe',
        ]
        for nom in domaines:
            CentreInteret.objects.get_or_create(
                nom=nom, categorie=CentreInteret.Categorie.DOMAINE
            )
        for nom in activites:
            CentreInteret.objects.get_or_create(
                nom=nom, categorie=CentreInteret.Categorie.ACTIVITE
            )

    def _formations(self):
        m = self.matieres
        gi, _ = Formation.objects.get_or_create(
            nom='Genie Informatique',
            defaults={
                'domaine': 'Informatique',
                'niveau': Formation.Niveau.INGENIEUR,
                'parcours': 'Prepa + Cycle Ingenieur',
                'description': (
                    "Formation d'ingenieur en informatique : developpement "
                    "logiciel, systemes, reseaux et sciences des donnees."
                ),
                'conditions_admission': 'Bac scientifique ou admission parallele Bac+2/Bac+3.',
                'competences_recherchees': 'Logique, algorithmique, rigueur, esprit d\'analyse.',
                'debouches': 'Developpeur, architecte logiciel, ingenieur DevOps, chef de projet.',
            },
        )
        gi.matieres_importantes.set([
            m['Mathematiques'], m['Informatique'], m['Physique'], m['Algorithmique'],
        ])
        PrerequisFormation.objects.get_or_create(
            formation=gi, matiere=m['Mathematiques'],
            defaults={'note_minimale': 12, 'poids': 3},
        )
        PrerequisFormation.objects.get_or_create(
            formation=gi, matiere=m['Informatique'],
            defaults={'note_minimale': 10, 'poids': 2},
        )

        gc, _ = Formation.objects.get_or_create(
            nom='Genie Civil',
            defaults={
                'domaine': 'Construction',
                'niveau': Formation.Niveau.INGENIEUR,
                'parcours': 'Prepa + Cycle Ingenieur',
                'description': "Conception et dimensionnement d'ouvrages, BTP, infrastructures.",
                'conditions_admission': 'Bac scientifique ou technique.',
                'competences_recherchees': 'Physique, mecanique, sens pratique.',
                'debouches': 'Ingenieur travaux, bureau d\'etudes, conducteur de travaux.',
            },
        )
        gc.matieres_importantes.set([
            m['Physique'], m['Mathematiques'], m['Mecanique'], m['Sciences techniques'],
        ])
        PrerequisFormation.objects.get_or_create(
            formation=gc, matiere=m['Physique'],
            defaults={'note_minimale': 12, 'poids': 3},
        )

        gind, _ = Formation.objects.get_or_create(
            nom='Genie Industriel',
            defaults={
                'domaine': 'Industriel',
                'niveau': Formation.Niveau.INGENIEUR,
                'parcours': 'Prepa + Cycle Ingenieur',
                'description': 'Optimisation des systemes de production, logistique, qualite.',
                'conditions_admission': 'Bac scientifique ou technique.',
                'competences_recherchees': 'Organisation, mathematiques appliquees, gestion.',
                'debouches': 'Ingenieur production, logisticien, consultant supply chain.',
            },
        )
        gind.matieres_importantes.set([
            m['Mathematiques'], m['Gestion'], m['Statistiques'], m['Mecanique'],
        ])
        PrerequisFormation.objects.get_or_create(
            formation=gind, matiere=m['Mathematiques'],
            defaults={'note_minimale': 11, 'poids': 2},
        )

        specs = [
            ('Web & Mobile', 'Developpement d\'applications web et mobiles.'),
            ('Cybersecurite', 'Securite des systemes d\'information et des reseaux.'),
            ('Data / Big Data / IA', 'Science des donnees, apprentissage automatique, IA.'),
        ]
        enfants = []
        for nom, desc in specs:
            f, _ = Formation.objects.get_or_create(
                nom=f'Genie Informatique - {nom}',
                defaults={
                    'domaine': 'Informatique',
                    'niveau': Formation.Niveau.INGENIEUR,
                    'parcours': 'Prepa + Cycle Ingenieur',
                    'parent': gi,
                    'description': desc,
                    'conditions_admission': 'Admission en cycle ingenieur, filiere GI.',
                    'debouches': 'Postes specialises en ' + nom + '.',
                },
            )
            f.matieres_importantes.set([m['Informatique'], m['Algorithmique'], m['Mathematiques']])
            enfants.append(f)

        licence, _ = Formation.objects.get_or_create(
            nom='Licence Informatique',
            defaults={
                'domaine': 'Informatique',
                'niveau': Formation.Niveau.LICENCE,
                'parcours': 'Licence + Master',
                'description': 'Licence fondamentale en informatique.',
                'conditions_admission': 'Baccalaureat.',
                'debouches': 'Poursuite en master ou insertion professionnelle.',
            },
        )
        licence.matieres_importantes.set([m['Informatique'], m['Mathematiques']])

        master, _ = Formation.objects.get_or_create(
            nom='Master Data Science',
            defaults={
                'domaine': 'Informatique',
                'niveau': Formation.Niveau.MASTER,
                'parcours': 'Licence + Master',
                'description': 'Master en science des donnees et intelligence artificielle.',
                'conditions_admission': 'Licence informatique, mathematiques ou equivalent.',
                'debouches': 'Data scientist, ML engineer, analyste.',
            },
        )
        master.matieres_importantes.set([m['Statistiques'], m['Informatique'], m['Mathematiques']])

        return {
            'gi': gi, 'gc': gc, 'gind': gind,
            'web': enfants[0], 'cyber': enfants[1], 'data': enfants[2],
            'licence': licence, 'master': master,
        }

    def _questionnaire(self, f):
        questionnaire, _ = Questionnaire.objects.get_or_create(
            titre="Questionnaire d'orientation ENSI",
            version=1,
            defaults={'est_actif': True},
        )
        if questionnaire.questions.exists():
            return

        def ajouter(texte, ordre, options):
            q = Question.objects.create(
                questionnaire=questionnaire, texte=texte, ordre=ordre
            )
            for libelle, ponderations in options:
                opt = OptionReponse.objects.create(question=q, texte=libelle)
                for formation, poids in ponderations:
                    PonderationOptionFormation.objects.create(
                        option=opt, formation=formation, poids=poids
                    )

        ajouter(
            'Dans un projet, quelle activite vous attire le plus ?', 1, [
                ('Analyser des donnees afin de comprendre un probleme.',
                 [(f['data'], 3), (f['master'], 2), (f['gi'], 1)]),
                ('Developper une solution informatique.',
                 [(f['gi'], 3), (f['web'], 3), (f['licence'], 2)]),
                ('Concevoir une solution physique ou structurelle.',
                 [(f['gc'], 3), (f['gind'], 1)]),
                ('Organiser les ressources et coordonner les personnes.',
                 [(f['gind'], 3), (f['gc'], 1)]),
            ],
        )
        ajouter(
            'Quel type de defi vous motive le plus ?', 2, [
                ('Proteger un systeme contre des attaques.',
                 [(f['cyber'], 3), (f['gi'], 2)]),
                ('Extraire de la valeur de grandes quantites de donnees.',
                 [(f['data'], 3), (f['master'], 3)]),
                ('Construire un ouvrage durable et sur.',
                 [(f['gc'], 3)]),
                ('Optimiser une chaine de production.',
                 [(f['gind'], 3)]),
            ],
        )
        ajouter(
            'Quel environnement de travail preferez-vous ?', 3, [
                ('Devant un ecran, a coder et tester.',
                 [(f['web'], 3), (f['gi'], 2), (f['licence'], 2)]),
                ('Sur le terrain, sur des chantiers ou en usine.',
                 [(f['gc'], 2), (f['gind'], 3)]),
                ('En laboratoire de recherche ou en analyse.',
                 [(f['data'], 2), (f['master'], 2)]),
                ('En reunion, a piloter des equipes.',
                 [(f['gind'], 2), (f['gc'], 1)]),
            ],
        )
        ajouter(
            'Quelle matiere preferez-vous approfondir ?', 4, [
                ('Algorithmique et programmation.',
                 [(f['gi'], 3), (f['web'], 2), (f['licence'], 2)]),
                ('Statistiques et probabilites.',
                 [(f['data'], 3), (f['master'], 3), (f['gind'], 1)]),
                ('Mecanique et resistance des materiaux.',
                 [(f['gc'], 3), (f['gind'], 1)]),
                ('Reseaux et securite.',
                 [(f['cyber'], 3), (f['gi'], 1)]),
            ],
        )
        ajouter(
            'Comment imaginez-vous votre carriere dans 10 ans ?', 5, [
                ('Expert technique reconnu dans le numerique.',
                 [(f['gi'], 2), (f['cyber'], 2), (f['data'], 2)]),
                ('Chef de projet sur de grands ouvrages.',
                 [(f['gc'], 3)]),
                ('Responsable production ou supply chain.',
                 [(f['gind'], 3)]),
                ('Chercheur ou data scientist.',
                 [(f['master'], 3), (f['data'], 2)]),
            ],
        )

    def _conseiller(self):
        user, created = Utilisateur.objects.get_or_create(
            email='conseiller@ensi-uma.tn',
            defaults={
                'first_name': 'Sami', 'last_name': 'Ben Ali',
                'role': Utilisateur.Role.CONSEILLER,
            },
        )
        if created:
            user.set_password('conseiller123')
            user.save()
        conseiller, _ = ProfilConseiller.objects.get_or_create(
            utilisateur=user,
            defaults={
                'specialite': 'Orientation scientifique et ingenierie',
                'biographie': "Conseiller d'orientation a l'ENSI depuis 10 ans.",
            },
        )
        maintenant = timezone.now().replace(minute=0, second=0, microsecond=0)
        for i in range(1, 6):
            debut = maintenant + timedelta(days=i, hours=9)
            DisponibiliteConseiller.objects.get_or_create(
                conseiller=conseiller,
                date_heure_debut=debut,
                defaults={'date_heure_fin': debut + timedelta(minutes=45)},
            )

    def _campagne(self):
        enseignant, _ = Enseignant.objects.get_or_create(
            nom='Trabelsi', prenom='Leila'
        )
        module, _ = Module.objects.get_or_create(
            code='ALGO1', defaults={'nom': 'Algorithmique et structures de donnees'}
        )
        groupe, _ = GroupeEtudiant.objects.get_or_create(
            nom='GI1-A', annee_universitaire='2025-2026'
        )
        campagne, created = CampagneEvaluation.objects.get_or_create(
            titre='Evaluation fin de module ALGO1',
            defaults={
                'enseignant': enseignant, 'module': module, 'groupe': groupe,
                'semestre': 'S1', 'statut': CampagneEvaluation.Statut.ACTIVE,
                'date_debut': timezone.now() - timedelta(days=1),
                'date_fin': timezone.now() + timedelta(days=30),
            },
        )
        if not created:
            return
        criteres = [
            'Qualite des explications', 'Maitrise du sujet', 'Disponibilite',
            'Interaction avec les etudiants', 'Respect du programme',
            'Qualite des supports', 'Satisfaction globale',
        ]
        for i, texte in enumerate(criteres, start=1):
            QuestionEvaluation.objects.create(
                campagne=campagne, texte=texte, ordre=i,
                type_question=QuestionEvaluation.TypeQuestion.NOTE,
            )
        QuestionEvaluation.objects.create(
            campagne=campagne, texte='Points positifs (facultatif)',
            ordre=8, type_question=QuestionEvaluation.TypeQuestion.TEXTE,
        )
        QuestionEvaluation.objects.create(
            campagne=campagne, texte='Points a ameliorer (facultatif)',
            ordre=9, type_question=QuestionEvaluation.TypeQuestion.TEXTE,
        )
        for email in ['etudiant1@ensi-uma.tn', 'etudiant2@ensi-uma.tn', 'etudiant3@ensi-uma.tn']:
            EvaluateurAutorise.objects.get_or_create(
                campagne=campagne, identifiant_anonyme=empreinte_email(email)
            )
