"""Catalogues marocains : filieres, specialites et matieres suggerees."""

# Baccalaureat (filieres officielles)
FILIERES_BAC = [
    ('sma', 'Sciences Math A'),
    ('smb', 'Sciences Math B'),
    ('pc', 'Sciences Physiques'),
    ('svt', 'Sciences de la Vie et de la Terre'),
    ('ste', 'Sciences et Technologies Electriques'),
    ('stm', 'Sciences et Technologies Mecaniques'),
    ('eco', 'Sciences Economiques'),
    ('sgc', 'Sciences de Gestion Comptable'),
    ('lettres', 'Lettres'),
    ('sh', 'Sciences Humaines'),
    ('arts', 'Arts Appliques'),
    ('sport', 'Education Physique'),
    ('agro', 'Sciences Agronomiques'),
]

# Bac+2 : famille d'etablissement puis specialite
TYPES_BAC2 = [
    ('fsjes', 'FSJES (Economie / Gestion / Droit)'),
    ('fst', 'FST (Sciences et Techniques)'),
    ('bts', 'BTS'),
    ('dut', 'DUT / DEUST'),
    ('cpge', 'CPGE (classes preparatoires)'),
    ('est', 'EST'),
    ('ofppt', 'OFPPT / Technicien specialise'),
]

SPECIALITES_BAC2 = {
    'fsjes': [
        ('eco', 'Economie'),
        ('gestion', 'Gestion'),
        ('droit', 'Droit'),
    ],
    'fst': [
        ('mip', 'MIP — Maths, Informatique, Physique'),
        ('bcg', 'BCG — Biologie, Chimie, Geologie'),
        ('ge', 'Genie Electrique'),
        ('gm', 'Genie Mecanique'),
        ('gi', 'Genie Informatique'),
    ],
    'bts': [
        ('info', 'Informatique'),
        ('compta', 'Comptabilite et gestion'),
        ('elec', 'Electrotechnique'),
        ('meca', 'Mecanique'),
        ('batiment', 'Batiment / Travaux publics'),
        ('commerce', 'Commerce international'),
    ],
    'dut': [
        ('info', 'Informatique'),
        ('gea', 'Gestion des entreprises'),
        ('gc', 'Genie civil'),
        ('ge', 'Genie electrique'),
    ],
    'cpge': [
        ('mpsi', 'MPSI / MP'),
        ('pcsi', 'PCSI / PC'),
        ('tsi', 'TSI'),
        ('ecs', 'ECS'),
        ('ect', 'ECT'),
    ],
    'est': [
        ('info', 'Genie informatique'),
        ('reseau', 'Reseaux et telecoms'),
        ('gc', 'Genie civil'),
        ('logistique', 'Logistique'),
    ],
    'ofppt': [
        ('dev', 'Developpement digital'),
        ('infra', 'Infrastructure digitale'),
        ('gestion', 'Gestion des entreprises'),
        ('btp', 'Batiment'),
    ],
}

TYPES_BAC3 = [
    ('fsjes', 'Licence FSJES'),
    ('fst', 'Licence FST / Faculte des sciences'),
    ('licence_pro', 'Licence professionnelle'),
    ('bachelor', 'Bachelor'),
]

SPECIALITES_BAC3 = {
    'fsjes': [
        ('eco', 'Economie et gestion'),
        ('finance', 'Finance'),
        ('marketing', 'Marketing'),
        ('droit', 'Droit'),
        ('logistique', 'Logistique'),
    ],
    'fst': [
        ('info', 'Informatique'),
        ('maths', 'Mathematiques'),
        ('physique', 'Physique'),
        ('chimie', 'Chimie'),
        ('gi', 'Genie informatique'),
        ('gc', 'Genie civil'),
    ],
    'licence_pro': [
        ('info', 'Informatique / digital'),
        ('gestion', 'Gestion / RH'),
        ('btp', 'BTP'),
        ('industrie', 'Industrie'),
    ],
    'bachelor': [
        ('info', 'Informatique'),
        ('business', 'Business / Management'),
        ('data', 'Data / IA'),
    ],
}

VILLES_MAROC = [
    'Tanger', 'Tetouan', 'Rabat', 'Sale', 'Casablanca', 'Mohammedia',
    'Kenitra', 'Fes', 'Meknes', 'Marrakech', 'Agadir', 'Oujda',
    'El Jadida', 'Nador', 'Laayoune', 'Beni Mellal',
]

ETABLISSEMENTS = {
    'fsjes': ['FSJES Tanger', 'FSJES Rabat-Agdal', 'FSJES Ain Chock', 'FSJES Fes', 'FSJES Marrakech'],
    'fst': ['FST Tanger', 'FST Mohammedia', 'FST Fes', 'FST Marrakech', 'FST Settat'],
    'bts': ['Lycee technique / BTS'],
    'dut': ['EST / FST — DUT-DEUST'],
    'cpge': ['CPGE Lycee', 'CPGE Privee'],
    'est': ['EST Tanger', 'EST Casablanca', 'EST Sale', 'EST Fes'],
    'ofppt': ['ISTA / OFPPT'],
}


def _uniq(noms):
    vus = []
    for nom in noms:
        if nom not in vus:
            vus.append(nom)
    return vus


MATIERES_BAC = {
    'sma': [
        'Mathematiques', 'Physique-Chimie', 'SVT', "Sciences de l'ingenieur",
        'Francais', 'Anglais', 'Philosophie', 'Education islamique',
    ],
    'smb': [
        'Mathematiques', 'Physique-Chimie', 'SVT', 'Francais', 'Anglais',
        'Philosophie', 'Education islamique',
    ],
    'pc': [
        'Mathematiques', 'Physique-Chimie', 'SVT', 'Francais', 'Anglais',
        'Philosophie', 'Education islamique',
    ],
    'svt': [
        'SVT', 'Physique-Chimie', 'Mathematiques', 'Francais', 'Anglais',
        'Philosophie', 'Education islamique',
    ],
    'ste': [
        'Mathematiques', 'Physique', "Sciences de l'ingenieur", 'Electrotechnique',
        'Francais', 'Anglais', 'Philosophie',
    ],
    'stm': [
        'Mathematiques', 'Physique', 'Mecanique', "Sciences de l'ingenieur",
        'Francais', 'Anglais', 'Philosophie',
    ],
    'eco': [
        'Economie', 'Mathematiques', 'Comptabilite', 'Philosophie',
        'Francais', 'Anglais', 'Histoire-Geographie',
    ],
    'sgc': [
        'Comptabilite', 'Economie', 'Gestion', 'Mathematiques',
        'Francais', 'Anglais', 'Philosophie',
    ],
    'lettres': [
        'Arabe', 'Francais', 'Philosophie', 'Histoire-Geographie',
        'Anglais', 'Education islamique',
    ],
    'sh': [
        'Histoire-Geographie', 'Philosophie', 'Arabe', 'Francais',
        'Anglais', 'Education islamique',
    ],
    'arts': ['Arts plastiques', 'Histoire de l\'art', 'Francais', 'Anglais', 'Philosophie'],
    'sport': ['Education physique', 'SVT', 'Philosophie', 'Francais', 'Anglais'],
    'agro': ['SVT', 'Physique-Chimie', 'Mathematiques', 'Agronomie', 'Francais', 'Anglais'],
}

MATIERES_BAC2 = {
    ('fsjes', 'eco'): [
        'Microeconomie', 'Macroeconomie', 'Statistiques', 'Mathematiques',
        'Comptabilite generale', 'Introduction au droit', 'Anglais',
    ],
    ('fsjes', 'gestion'): [
        'Comptabilite generale', 'Comptabilite analytique', 'Management',
        'Marketing', 'Statistiques', 'Droit commercial', 'Anglais',
    ],
    ('fsjes', 'droit'): [
        'Droit constitutionnel', 'Droit civil', 'Droit penal',
        'Introduction a l\'economie', 'Arabe juridique', 'Francais juridique',
    ],
    ('fst', 'mip'): [
        'Mathematiques', 'Physique', 'Informatique', 'Chimie',
        'Algorithmique', 'Anglais scientifique',
    ],
    ('fst', 'bcg'): [
        'Biologie', 'Chimie', 'Geologie', 'Mathematiques', 'Physique',
    ],
    ('fst', 'ge'): [
        'Electrotechnique', 'Electronique', 'Mathematiques', 'Physique', 'Informatique',
    ],
    ('fst', 'gm'): [
        'Mecanique', 'Resistance des materiaux', 'Mathematiques', 'Physique', 'CAO',
    ],
    ('fst', 'gi'): [
        'Algorithmique', 'Programmation', 'Bases de donnees',
        'Mathematiques', 'Architecture des ordinateurs', 'Anglais',
    ],
    ('bts', 'info'): [
        'Algorithmique', 'Programmation', 'Bases de donnees',
        'Reseaux', 'Systemes d\'exploitation', 'Mathematiques',
    ],
    ('bts', 'compta'): [
        'Comptabilite generale', 'Comptabilite analytique', 'Fiscalite',
        'Gestion', 'Statistiques', 'Droit',
    ],
    ('bts', 'elec'): [
        'Electrotechnique', 'Electronique', 'Automatisme', 'Mathematiques', 'Physique',
    ],
    ('bts', 'meca'): [
        'Mecanique', 'Fabrication', 'CAO', 'Mathematiques', 'Physique',
    ],
    ('bts', 'batiment'): [
        'Resistance des materiaux', 'Dessin technique', 'Topographie',
        'Materiaux de construction', 'Mathematiques',
    ],
    ('bts', 'commerce'): [
        'Commerce international', 'Marketing', 'Economie', 'Anglais', 'Comptabilite',
    ],
    ('dut', 'info'): [
        'Algorithmique', 'Programmation', 'Bases de donnees', 'Reseaux', 'Mathematiques',
    ],
    ('dut', 'gea'): [
        'Comptabilite generale', 'Management', 'Economie', 'Statistiques', 'Droit',
    ],
    ('dut', 'gc'): [
        'Resistance des materiaux', 'Beton', 'Topographie', 'Mathematiques', 'Physique',
    ],
    ('dut', 'ge'): [
        'Electrotechnique', 'Electronique', 'Automatisme', 'Mathematiques',
    ],
    ('cpge', 'mpsi'): [
        'Mathematiques', 'Physique', 'Sciences de l\'ingenieur', 'Informatique', 'Francais', 'Anglais',
    ],
    ('cpge', 'pcsi'): [
        'Mathematiques', 'Physique', 'Chimie', 'Sciences de l\'ingenieur', 'Francais', 'Anglais',
    ],
    ('cpge', 'tsi'): [
        'Mathematiques', 'Physique', 'Sciences de l\'ingenieur', 'Francais', 'Anglais',
    ],
    ('cpge', 'ecs'): [
        'Mathematiques', 'Histoire-Geographie', 'Economie', 'Philosophie', 'Langues',
    ],
    ('cpge', 'ect'): [
        'Mathematiques', 'Economie', 'Droit', 'Management', 'Langues',
    ],
    ('est', 'info'): [
        'Programmation', 'Bases de donnees', 'Reseaux', 'Mathematiques', 'Systeme',
    ],
    ('est', 'reseau'): [
        'Reseaux', 'Telecoms', 'Systemes', 'Mathematiques', 'Electronique',
    ],
    ('est', 'gc'): [
        'Resistance des materiaux', 'Topographie', 'Dessin technique', 'Mathematiques',
    ],
    ('est', 'logistique'): [
        'Logistique', 'Gestion de production', 'Statistiques', 'Economie', 'Anglais',
    ],
    ('ofppt', 'dev'): [
        'Programmation web', 'Bases de donnees', 'Algorithmique', 'UI/UX', 'Anglais',
    ],
    ('ofppt', 'infra'): [
        'Reseaux', 'Systemes', 'Securite', 'Virtualisation', 'Anglais',
    ],
    ('ofppt', 'gestion'): [
        'Comptabilite', 'Management', 'Bureautique', 'Communication', 'Anglais',
    ],
    ('ofppt', 'btp'): [
        'Dessin technique', 'Materiaux', 'Topographie', 'Securite chantier',
    ],
}

MATIERES_BAC3 = {
    ('fsjes', 'eco'): [
        'Microeconomie approfondie', 'Macroeconomie', 'Econometrie',
        'Statistiques', 'Comptabilite nationale', 'Anglais des affaires',
    ],
    ('fsjes', 'finance'): [
        'Finance d\'entreprise', 'Marches financiers', 'Comptabilite',
        'Statistiques', 'Fiscalite', 'Anglais',
    ],
    ('fsjes', 'marketing'): [
        'Marketing strategique', 'Etudes de marche', 'Communication',
        'Statistiques', 'Comportement du consommateur', 'Anglais',
    ],
    ('fsjes', 'droit'): [
        'Droit des affaires', 'Droit administratif', 'Droit du travail',
        'Procedure', 'Francais juridique',
    ],
    ('fsjes', 'logistique'): [
        'Supply chain', 'Transport', 'Gestion des stocks', 'Statistiques', 'Anglais',
    ],
    ('fst', 'info'): [
        'Algorithmique avancee', 'POO', 'Bases de donnees',
        'Reseaux', 'Systeme d\'exploitation', 'Mathematiques',
    ],
    ('fst', 'maths'): [
        'Algebre', 'Analyse', 'Probabilites', 'Statistiques', 'Informatique',
    ],
    ('fst', 'physique'): [
        'Mecanique', 'Electromagnetisme', 'Thermodynamique', 'Mathematiques', 'TP Physique',
    ],
    ('fst', 'chimie'): [
        'Chimie organique', 'Chimie minerale', 'Chimie analytique', 'Mathematiques',
    ],
    ('fst', 'gi'): [
        'Genie logiciel', 'Bases de donnees', 'Reseaux', 'Compilation', 'Projet',
    ],
    ('fst', 'gc'): [
        'Beton arme', 'Mecanique des sols', 'Structures', 'Topographie', 'DAO',
    ],
    ('licence_pro', 'info'): [
        'Developpement', 'Bases de donnees', 'Reseaux', 'Projet professionnel', 'Anglais',
    ],
    ('licence_pro', 'gestion'): [
        'GRH', 'Comptabilite', 'Management', 'Droit social', 'Anglais',
    ],
    ('licence_pro', 'btp'): [
        'Chantier', 'Structures', 'Gestion de projet', 'DAO', 'Securite',
    ],
    ('licence_pro', 'industrie'): [
        'Production', 'Qualite', 'Maintenance', 'Lean', 'Statistiques',
    ],
    ('bachelor', 'info'): [
        'Programmation', 'Web', 'Bases de donnees', 'Projet', 'Anglais',
    ],
    ('bachelor', 'business'): [
        'Management', 'Marketing', 'Finance', 'Strategie', 'Anglais',
    ],
    ('bachelor', 'data'): [
        'Statistiques', 'Python', 'Machine learning', 'Bases de donnees', 'Anglais',
    ],
}


def types_pour(niveau):
    if niveau == 'bac':
        return FILIERES_BAC
    if niveau == 'bac2':
        return TYPES_BAC2
    if niveau == 'bac3':
        return TYPES_BAC3
    return []


def specialites_pour(niveau, type_diplome):
    if niveau == 'bac':
        return []
    table = SPECIALITES_BAC2 if niveau == 'bac2' else SPECIALITES_BAC3
    return table.get(type_diplome, [])


def matieres_pour(niveau, type_diplome, specialite=''):
    if not type_diplome:
        return []
    if niveau == 'bac':
        return list(MATIERES_BAC.get(type_diplome, MATIERES_BAC['pc']))
    table = MATIERES_BAC2 if niveau == 'bac2' else MATIERES_BAC3
    cle = (type_diplome, specialite)
    if cle in table:
        return list(table[cle])
    # fallback : premiere specialite du type
    for (typ, spec), noms in table.items():
        if typ == type_diplome:
            return list(noms)
    return ['Mathematiques', 'Francais', 'Anglais']


def toutes_matieres():
    noms = []
    for liste in MATIERES_BAC.values():
        noms.extend(liste)
    for liste in MATIERES_BAC2.values():
        noms.extend(liste)
    for liste in MATIERES_BAC3.values():
        noms.extend(liste)
    noms += [
        'Informatique', 'Algorithmique', 'Statistiques', 'Gestion',
        'Sciences techniques', 'Physique',
    ]
    return _uniq(noms)


def etablissements_pour(type_diplome):
    return ETABLISSEMENTS.get(type_diplome, [])
