PLATFORM_NAMES = ["Facebook", "Instagram", "TikTok", "YouTube"]
REFERENCE_BASE_DATE = "3 août 2026"

UNKNOWN_NETWORK = "Je ne sais pas"
OUT_OF_SCOPE_NETWORK = "Aucun de ces réseaux : Facebook, Instagram, TikTok ou YouTube"

PROFILE_OPTIONS = [
    "Créateur d’entreprise",
    "Micro-entrepreneur",
    "Artisan / commerçant / restaurateur",
    "Dirigeant TPE-PME",
    "Start-up",
    "Profession libérale / Freelance",
    "Association / Secteur non-marchand",
    "Jeune talent / étudiant",
    "Jeune particulier / premier projet patrimonial",
    "Particulier / retraite ou transmission patrimoniale",
    "Autre",
]

TARGET_NETWORK_OPTIONS = PLATFORM_NAMES + [UNKNOWN_NETWORK, OUT_OF_SCOPE_NETWORK]

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

EVIDENCE_QUALITY_OPTIONS = ["Oui", "Non"]

OBJECTIVE_OPTIONS = [
    "Visibilité et notoriété",
    "Acquisition",
    "Expertise et conseil",
    "Recrutement",
    "Fidélisation",
    "Autre",
    "Non défini",
]

INDICATOR_OPTIONS = [
    "Portée des publications",
    "Visites du profil ou du site",
    "Interactions avec les publications",
    "Enregistrements ou partages des contenus",
    "Demandes de contact",
    "Rendez-vous obtenus",
    "Lettres de mission signées",
    "Candidatures reçues",
    "Entretiens de recrutement obtenus",
    "Demandes de clients existants",
    "Chiffre d’affaires généré",
    "Autre indicateur",
]

INDICATORS_BY_OBJECTIVE = {
    "Visibilité et notoriété": [
        "Portée des publications",
        "Visites du profil ou du site",
        "Interactions avec les publications",
        "Enregistrements ou partages des contenus",
        "Autre indicateur",
    ],
    "Acquisition": [
        "Demandes de contact",
        "Rendez-vous obtenus",
        "Lettres de mission signées",
        "Chiffre d’affaires généré",
        "Autre indicateur",
    ],
    "Expertise et conseil": [
        "Visites du profil ou du site",
        "Interactions avec les publications",
        "Enregistrements ou partages des contenus",
        "Demandes de contact",
        "Autre indicateur",
    ],
    "Recrutement": [
        "Candidatures reçues",
        "Entretiens de recrutement obtenus",
        "Autre indicateur",
    ],
    "Fidélisation": [
        "Interactions avec les publications",
        "Demandes de clients existants",
        "Autre indicateur",
    ],
    "Autre": INDICATOR_OPTIONS.copy(),
}

TIME_OPTIONS = [
    "Aucun temps disponible",
    "Moins de 2 h",
    "2 à 5 h",
    "6 à 10 h",
    "Plus de 10 h",
]

COMPETENCY_LEVELS = ["À acquérir", "Notions", "Autonome"]

GENERIC_FORMATS = [
    "Publication texte",
    "Photo",
    "Carrousel",
    "Vidéo courte",
    "Vidéo longue",
    "Story",
    "Live",
]

EQUIPMENT_OPTIONS = [
    "Smartphone récent",
    "Caméra",
    "Ordinateur",
    "Connexion internet stable",
    "Micro",
    "Ring light",
    "Studio équipé",
    "Autre matériel",
    "Aucun matériel",
]

PILOT_OPTIONS = [
    "L’expert-comptable",
    "Un associé",
    "Un collaborateur désigné",
    "Une personne ou équipe dédiée à la communication",
    "Un community manager ou prestataire externe",
    "Autre",
]

NO_PILOT = "Personne n’est encore désignée"

APP_SUPPORT_OPTIONS = [
    "Autoformation",
    "Formation",
    "Appui interne",
    "Prestataire externe",
]

SUPPORT_CONFIRMATION_LABELS = {
    "Autoformation": "Cette autoformation est-elle planifiée ?",
    "Formation": "Cette formation est-elle choisie ou planifiée ?",
    "Appui interne": "La personne qui apportera cet appui est-elle identifiée et disponible ?",
    "Prestataire externe": "Le prestataire est-il choisi et disponible ?",
}

# Référentiel d'appui utilisé avec les observations du cabinet et la recherche
# externe. Une plateforme absente de cette liste n'est jamais considérée comme
# impossible : elle dispose seulement de moins d'indices favorables au départ.
PERSONA_PLATFORM_REFERENCE = {
    "Créateur d’entreprise": ["YouTube", "Instagram", "TikTok", "Facebook"],
    "Micro-entrepreneur": ["Instagram", "Facebook", "TikTok", "YouTube"],
    "Artisan / commerçant / restaurateur": ["Facebook", "Instagram", "TikTok", "YouTube"],
    "Dirigeant TPE-PME": ["YouTube", "Facebook", "Instagram", "TikTok"],
    "Start-up": ["Instagram", "TikTok", "YouTube", "Facebook"],
    "Profession libérale / Freelance": ["Instagram", "YouTube", "TikTok", "Facebook"],
    "Association / Secteur non-marchand": ["Facebook", "Instagram", "YouTube", "TikTok"],
    "Jeune talent / étudiant": ["TikTok", "Instagram", "YouTube", "Facebook"],
    "Jeune particulier / premier projet patrimonial": ["TikTok", "Instagram", "YouTube", "Facebook"],
    "Particulier / retraite ou transmission patrimoniale": ["YouTube", "Facebook", "Instagram", "TikTok"],
    "Autre": PLATFORM_NAMES.copy(),
}

OBJECTIVE_PRIORITY_PLATFORMS = {
    "Visibilité et notoriété": ["Instagram", "TikTok", "Facebook", "YouTube"],
    "Acquisition": ["Facebook", "Instagram", "YouTube", "TikTok"],
    "Expertise et conseil": ["YouTube", "Instagram", "Facebook", "TikTok"],
    "Recrutement": ["Instagram", "TikTok", "Facebook", "YouTube"],
    "Fidélisation": ["Facebook", "Instagram", "YouTube", "TikTok"],
    "Autre": PLATFORM_NAMES.copy(),
}

# Le besoin prioritaire est classé dans une famille fonctionnelle. Ces familles
# servent à rechercher et à comparer les plateformes, sans demander une étude
# comportementale supplémentaire à l'utilisateur.
NEED_CATEGORY_KEYWORDS = {
    "explication approfondie": [
        "statut", "société", "sasu", "eurl", "choisir", "compar", "transform",
        "passer de", "fiscal", "juridique", "patrimoine", "transmission", "retraite",
        "rentabilité", "financement", "business plan", "décision", "arbitr",
    ],
    "démarche pratique": [
        "comment", "étape", "démarche", "formal", "procédure", "checklist", "liste",
        "créer", "immatric", "déclar", "mettre en place", "organiser", "outil",
    ],
    "actualité et échéance": [
        "actualité", "réforme", "nouveau", "échéance", "date", "obligation", "loi",
        "déclaration", "calendrier", "taux", "seuil", "changement",
    ],
    "confiance et réassurance": [
        "peur", "risque", "erreur", "éviter", "sécur", "confiance", "rassur",
        "idée reçue", "comprendre", "pourquoi", "accompagnement",
    ],
    "recrutement": [
        "recrut", "candidat", "emploi", "altern", "stage", "collaborateur", "talent",
    ],
    "fidélisation": [
        "fidél", "client existant", "suivi", "relation client", "rappel", "accompagner dans le temps",
    ],
    "découverte": [
        "connaître", "découvrir", "visibilité", "notoriété", "présenter", "sensibiliser",
        "faire connaître", "attirer l'attention",
    ],
}

NEED_PLATFORM_PRIORITY = {
    "explication approfondie": ["YouTube", "Instagram", "Facebook", "TikTok"],
    "démarche pratique": ["YouTube", "Instagram", "TikTok", "Facebook"],
    "actualité et échéance": ["Facebook", "Instagram", "TikTok", "YouTube"],
    "confiance et réassurance": ["YouTube", "Instagram", "Facebook", "TikTok"],
    "recrutement": ["Instagram", "TikTok", "Facebook", "YouTube"],
    "fidélisation": ["Facebook", "Instagram", "YouTube", "TikTok"],
    "découverte": ["Instagram", "TikTok", "Facebook", "YouTube"],
    "général": PLATFORM_NAMES.copy(),
}

PLATFORM_ROLES = {
    "Facebook": "information de proximité, communauté et relation suivie",
    "Instagram": "visibilité visuelle, pédagogie synthétique et proximité",
    "TikTok": "découverte rapide, sensibilisation et formats courts",
    "YouTube": "explication approfondie, démonstration et contenu durable",
}

PLATFORM_FORMATS = {
    "Facebook": {
        "Publication texte", "Photo", "Carrousel", "Vidéo courte",
        "Vidéo longue", "Story", "Live",
    },
    "Instagram": {"Photo", "Carrousel", "Vidéo courte", "Story", "Live"},
    "TikTok": {"Photo", "Carrousel", "Vidéo courte", "Vidéo longue", "Story", "Live"},
    "YouTube": {"Publication texte", "Photo", "Vidéo courte", "Vidéo longue", "Live"},
}

# Au moins un format structurant est nécessaire. Un second format compatible est
# demandé pour éviter une communication durablement enfermée dans un seul format.
PLATFORM_ESSENTIAL_FORMATS = {
    "Facebook": {"Publication texte", "Photo", "Carrousel", "Vidéo courte"},
    "Instagram": {"Carrousel", "Vidéo courte", "Photo"},
    "TikTok": {"Vidéo courte", "Vidéo longue"},
    "YouTube": {"Vidéo courte", "Vidéo longue", "Live"},
}

PLATFORM_MINIMUM_TIME = {
    "Facebook": "2 à 5 h",
    "Instagram": "2 à 5 h",
    "TikTok": "2 à 5 h",
    "YouTube": "6 à 10 h",
}

# Une plateforme complémentaire n'est proposée que si le contenu principal peut
# être adapté sans créer une seconde ligne éditoriale complète.
CONTENT_REUSE_PAIRS = {
    ("YouTube", "Instagram"),
    ("YouTube", "TikTok"),
    ("YouTube", "Facebook"),
    ("Instagram", "Facebook"),
    ("Instagram", "TikTok"),
    ("TikTok", "Instagram"),
    ("Facebook", "Instagram"),
}

FORMAT_REQUIRED_SKILLS = {
    "Publication texte": {"Rédaction / script"},
    "Photo": {"Création de visuels"},
    "Carrousel": {"Rédaction / script", "Création de visuels"},
    "Vidéo courte": {"Rédaction / script", "Montage vidéo"},
    "Vidéo longue": {"Rédaction / script", "Montage vidéo"},
    "Story": {"Rédaction / script", "Création de visuels"},
    "Live": {"Rédaction / script", "Aisance face caméra"},
}

VIDEO_FORMATS = {"Vidéo courte", "Vidéo longue", "Live"}
VISUAL_FORMATS = {"Photo", "Carrousel", "Story"}
