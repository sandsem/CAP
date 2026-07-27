PLATFORM_NAMES = ["Facebook", "Instagram", "TikTok", "YouTube"]

PROFILE_OPTIONS = [
    "Créateur d’entreprise",
    "Micro-entrepreneur",
    "Artisan / commerçant / restaurateur",
    "Dirigeant TPE-PME",
    "Start-up",
    "Profession libérale / Freelance",
    "Association / Secteur non-marchand",
    "Jeune talent / étudiant",
    "Particulier / Gestion de patrimoine",
    "Autre",
    "Non identifié",
]

TARGET_NETWORK_OPTIONS = [
    "Facebook",
    "Instagram",
    "TikTok",
    "YouTube",
    "Autre réseau",
    "Non identifié",
]

SOURCE_OPTIONS = [
    "Expérience terrain",
    "Données clients",
    "Entretiens",
    "Questionnaire",
    "Étude sectorielle",
    "Statistiques",
    "Autre source",
    "Aucune source",
]

OBJECTIVE_OPTIONS = [
    "Visibilité / notoriété",
    "Acquisition",
    "Expertise / conseil",
    "Recrutement",
    "Fidélisation",
    "Autre",
    "Non défini",
]

INDICATOR_OPTIONS = {
    "Visibilité / notoriété": [
        "Portée",
        "Impressions",
        "Vues",
        "Visites du profil",
        "Nouveaux abonnés",
        "Autre indicateur",
    ],
    "Acquisition": [
        "Prises de contact qualifiées",
        "Rendez-vous obtenus",
        "Lettres de mission signées",
        "Chiffre d’affaires généré",
        "Autre indicateur",
    ],
    "Expertise / conseil": [
        "Enregistrements",
        "Partages",
        "Temps de visionnage",
        "Demandes de conseil",
        "Autre indicateur",
    ],
    "Recrutement": [
        "Candidatures reçues",
        "Candidatures qualifiées",
        "Entretiens obtenus",
        "Recrutements finalisés",
        "Autre indicateur",
    ],
    "Fidélisation": [
        "Interactions clients",
        "Questions reçues",
        "Missions complémentaires",
        "Taux de rétention",
        "Autre indicateur",
    ],
    "Autre": ["Autre indicateur"],
}

PLATFORM_STATUS_OPTIONS = [
    "Aucun compte",
    "Compte inactif",
    "Compte actif",
    "Audience cible engagée",
    "Contacts obtenus",
]

TIME_OPTIONS = [
    "Moins de 2 h",
    "2 à 5 h",
    "6 à 10 h",
    "Plus de 10 h",
    "Non évalué",
]

COMPETENCY_LEVELS = ["À acquérir", "Notions", "Autonome"]

EQUIPMENT_OPTIONS = [
    "Smartphone récent",
    "Caméra",
    "Ordinateur",
    "Connexion stable",
    "Micro",
    "Ring light",
    "Studio équipé",
    "Autre matériel",
    "Aucun matériel",
]

PILOT_OPTIONS = [
    "Expert-comptable",
    "Associé",
    "Expert et associé",
    "Collaborateur référent",
    "Prestataire externe",
    "Service communication",
    "Non défini",
]

APP_SUPPORT_OPTIONS = [
    "Autoformation",
    "Formation",
    "Appui interne",
    "Prestataire externe",
    "Autre solution",
    "Aucun appui",
    "Non défini",
]

BUDGET_OPTIONS = [
    "Aucun budget",
    "Moins de 50 €",
    "50 à 150 €",
    "Plus de 150 €",
    "Non évalué",
]


# Les valeurs expriment une affinité sur 100. Elles sont ensuite pondérées
# dans scoring.py. La matrice reste séparée de l'interface pour pouvoir être
# auditée et ajustée sans modifier le parcours utilisateur.
PROFILE_AFFINITY = {
    "Créateur d’entreprise": {
        "Facebook": 85,
        "Instagram": 90,
        "TikTok": 90,
        "YouTube": 85,
    },
    "Micro-entrepreneur": {
        "Facebook": 90,
        "Instagram": 85,
        "TikTok": 95,
        "YouTube": 70,
    },
    "Artisan / commerçant / restaurateur": {
        "Facebook": 100,
        "Instagram": 85,
        "TikTok": 70,
        "YouTube": 55,
    },
    "Dirigeant TPE-PME": {
        "Facebook": 90,
        "Instagram": 75,
        "TikTok": 45,
        "YouTube": 80,
    },
    "Start-up": {
        "Facebook": 55,
        "Instagram": 100,
        "TikTok": 85,
        "YouTube": 80,
    },
    "Profession libérale / Freelance": {
        "Facebook": 70,
        "Instagram": 95,
        "TikTok": 90,
        "YouTube": 75,
    },
    "Association / Secteur non-marchand": {
        "Facebook": 100,
        "Instagram": 65,
        "TikTok": 55,
        "YouTube": 60,
    },
    "Jeune talent / étudiant": {
        "Facebook": 45,
        "Instagram": 90,
        "TikTok": 100,
        "YouTube": 75,
    },
    "Particulier / Gestion de patrimoine": {
        "Facebook": 90,
        "Instagram": 70,
        "TikTok": 55,
        "YouTube": 85,
    },
    "Autre": {
        "Facebook": 50,
        "Instagram": 50,
        "TikTok": 50,
        "YouTube": 50,
    },
}

OBJECTIVE_AFFINITY = {
    "Visibilité / notoriété": {
        "Facebook": 75,
        "Instagram": 90,
        "TikTok": 100,
        "YouTube": 75,
    },
    "Acquisition": {
        "Facebook": 85,
        "Instagram": 90,
        "TikTok": 75,
        "YouTube": 80,
    },
    "Expertise / conseil": {
        "Facebook": 80,
        "Instagram": 75,
        "TikTok": 65,
        "YouTube": 100,
    },
    "Recrutement": {
        "Facebook": 55,
        "Instagram": 85,
        "TikTok": 85,
        "YouTube": 60,
    },
    "Fidélisation": {
        "Facebook": 100,
        "Instagram": 85,
        "TikTok": 55,
        "YouTube": 70,
    },
    "Autre": {
        "Facebook": 50,
        "Instagram": 50,
        "TikTok": 50,
        "YouTube": 50,
    },
}

TIME_AFFINITY = {
    "Moins de 2 h": {
        "Facebook": 100,
        "Instagram": 55,
        "TikTok": 40,
        "YouTube": 10,
    },
    "2 à 5 h": {
        "Facebook": 90,
        "Instagram": 75,
        "TikTok": 65,
        "YouTube": 30,
    },
    "6 à 10 h": {
        "Facebook": 80,
        "Instagram": 95,
        "TikTok": 90,
        "YouTube": 65,
    },
    "Plus de 10 h": {
        "Facebook": 75,
        "Instagram": 95,
        "TikTok": 95,
        "YouTube": 100,
    },
    "Non évalué": {
        "Facebook": 50,
        "Instagram": 50,
        "TikTok": 50,
        "YouTube": 50,
    },
}

# La cible prime. Les réseaux qu'elle utilise représentent donc le poids
# le plus important. Le compte du cabinet n'est pas inclus ici.
COHERENCE_WEIGHTS = {
    "profile": 0.25,
    "target_networks": 0.40,
    "objective": 0.20,
    "time": 0.15,
}

STATUS_TIE_BREAK = {
    "Aucun compte": 0,
    "Compte inactif": 0,
    "Compte actif": 0,
    "Audience cible engagée": 1.5,
    "Contacts obtenus": 2.0,
}
