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

EVIDENCE_QUALITY_OPTIONS = [
    "Récentes et fiables",
    "Partiellement vérifiées",
    "Anciennes ou non vérifiées",
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

DISCOVERY_MODE_OPTIONS = [
    "Recherche volontaire d’une réponse",
    "Échanges dans une communauté ou un groupe local",
    "Découverte visuelle en suivant des comptes",
    "Recommandation de contenus selon les centres d’intérêt",
    "Non identifié",
]

EDITORIAL_TREATMENT_OPTIONS = [
    "Informer et échanger avec une communauté",
    "Montrer et vulgariser visuellement",
    "Capter rapidement avec un contenu direct et incarné",
    "Expliquer et approfondir un sujet",
    "Non défini",
]

AUDIENCE_EFFECT_OPTIONS = [
    "Créer une relation de proximité",
    "Valoriser l’image du cabinet et entretenir la relation",
    "Faire découvrir le cabinet",
    "Démontrer l’expertise et répondre à un besoin identifié",
    "Non défini",
]

PLATFORM_STATUS_OPTIONS = [
    "Aucun compte",
    "Compte inactif",
    "Compte actif",
    "Audience cible engagée",
    "Contacts obtenus",
]

TIME_OPTIONS = [
    "Aucun temps disponible",
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
    "Aide interne",
    "Prestataire",
    "Autre solution",
    "Solution à trouver",
]

BUDGET_OPTIONS = [
    "Aucune dépense nécessaire",
    "Oui",
    "À vérifier",
    "Non",
]

# Cette grille décrit les différences de fonctionnement des plateformes.
# Elle ne contient ni note sur 100, ni pondération, ni hypothèse liée à l’âge
# ou au métier du persona. Le profil sert à décrire la cible ; son comportement
# réel sert à comparer les réseaux qu’elle utilise.
PLATFORM_REFERENCE = {
    "Facebook": {
        "discovery_modes": {"Échanges dans une communauté ou un groupe local"},
        "editorial_treatment": "Informer et échanger avec une communauté",
        "audience_effect": "Créer une relation de proximité",
        "objectives": {
            "Visibilité / notoriété",
            "Acquisition",
            "Fidélisation",
        },
        "discovery_label": "communautés, groupes et proximité territoriale",
        "treatment_label": "information et échange",
        "effect_label": "relation de proximité",
    },
    "Instagram": {
        "discovery_modes": {"Découverte visuelle en suivant des comptes"},
        "editorial_treatment": "Montrer et vulgariser visuellement",
        "audience_effect": "Valoriser l’image du cabinet et entretenir la relation",
        "objectives": {
            "Visibilité / notoriété",
            "Acquisition",
            "Recrutement",
            "Fidélisation",
        },
        "discovery_label": "découverte visuelle et suivi des comptes",
        "treatment_label": "mise en valeur et vulgarisation",
        "effect_label": "valorisation de l’image et entretien de la relation",
    },
    "TikTok": {
        "discovery_modes": {
            "Recommandation de contenus selon les centres d’intérêt"
        },
        "editorial_treatment": "Capter rapidement avec un contenu direct et incarné",
        "audience_effect": "Faire découvrir le cabinet",
        "objectives": {
            "Visibilité / notoriété",
            "Acquisition",
            "Recrutement",
        },
        "discovery_label": "recommandation selon les centres d’intérêt",
        "treatment_label": "contenu direct et incarné",
        "effect_label": "découverte du cabinet",
    },
    "YouTube": {
        "discovery_modes": {
            "Recherche volontaire d’une réponse",
            "Recommandation de contenus selon les centres d’intérêt",
        },
        "editorial_treatment": "Expliquer et approfondir un sujet",
        "audience_effect": "Démontrer l’expertise et répondre à un besoin identifié",
        "objectives": {
            "Visibilité / notoriété",
            "Acquisition",
            "Expertise / conseil",
        },
        "discovery_label": "recherche volontaire et recommandation",
        "treatment_label": "explication structurée",
        "effect_label": "démonstration de l’expertise",
    },
}

PLATFORM_FORMATS = {
    "Facebook": [
        "Publication texte",
        "Photo / visuel",
        "Carrousel",
        "Reel / vidéo courte",
        "Story",
        "Live",
    ],
    "Instagram": [
        "Photo",
        "Carrousel",
        "Reel",
        "Story",
        "Live",
    ],
    "TikTok": [
        "Vidéo",
        "Publication photo / carrousel",
        "Story",
        "Live",
    ],
    "YouTube": [
        "Vidéo longue",
        "Short",
        "Live",
        "Publication Communauté",
    ],
}

FORMAT_REQUIRED_SKILLS = {
    "Publication texte": {"Rédaction / script"},
    "Photo / visuel": {"Rédaction / script", "Création de visuels"},
    "Photo": {"Rédaction / script", "Création de visuels"},
    "Carrousel": {"Rédaction / script", "Création de visuels"},
    "Publication photo / carrousel": {
        "Rédaction / script",
        "Création de visuels",
    },
    "Publication Communauté": {
        "Rédaction / script",
        "Création de visuels",
    },
    "Reel / vidéo courte": {"Rédaction / script", "Montage vidéo"},
    "Reel": {"Rédaction / script", "Montage vidéo"},
    "Vidéo": {"Rédaction / script", "Montage vidéo"},
    "Vidéo longue": {
        "Rédaction / script",
        "Montage vidéo",
    },
    "Short": {"Rédaction / script", "Montage vidéo"},
    "Story": {"Rédaction / script", "Création de visuels"},
    "Live": {"Rédaction / script", "Aisance face caméra"},
}

VIDEO_FORMATS = {
    "Reel / vidéo courte",
    "Reel",
    "Vidéo",
    "Vidéo longue",
    "Short",
    "Live",
}

VISUAL_FORMATS = {
    "Photo / visuel",
    "Photo",
    "Carrousel",
    "Publication photo / carrousel",
    "Publication Communauté",
    "Story",
}
