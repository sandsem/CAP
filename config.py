PLATFORM_NAMES = ["Facebook", "Instagram", "TikTok", "YouTube"]
REFERENCE_BASE_DATE = "31 juillet 2026"

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
    "Demandes de contact",
    "Rendez-vous obtenus",
    "Lettres de mission signées",
    "Candidatures reçues",
    "Chiffre d’affaires généré",
    "Autre indicateur",
]

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

# Base de référence utilisée uniquement lorsque le cabinet ne connaît pas encore
# les réseaux réellement utilisés par son persona. Elle doit être datée et revue
# périodiquement dans la documentation de l'outil.
PERSONA_PLATFORM_REFERENCE = {
    "Créateur d’entreprise": ["YouTube", "Instagram", "TikTok"],
    "Micro-entrepreneur": ["Instagram", "Facebook", "TikTok"],
    "Artisan / commerçant / restaurateur": ["Facebook", "Instagram", "TikTok"],
    "Dirigeant TPE-PME": ["YouTube", "Facebook", "Instagram"],
    "Start-up": ["Instagram", "TikTok", "YouTube"],
    "Profession libérale / Freelance": ["Instagram", "YouTube", "TikTok"],
    "Association / Secteur non-marchand": ["Facebook", "Instagram", "YouTube"],
    "Jeune talent / étudiant": ["TikTok", "Instagram", "YouTube"],
    "Jeune particulier / premier projet patrimonial": ["TikTok", "Instagram", "YouTube"],
    "Particulier / retraite ou transmission patrimoniale": ["YouTube", "Facebook", "Instagram"],
    # Pour un persona libre, l'outil ne suppose pas une audience qu'il ne connaît pas.
    "Autre": PLATFORM_NAMES.copy(),
}

# Une priorité ne signifie jamais que les autres plateformes sont incapables de
# servir l'objectif. Elle sert uniquement à départager plusieurs réseaux possibles.
OBJECTIVE_PRIORITY_PLATFORMS = {
    "Visibilité et notoriété": {"Instagram", "TikTok"},
    "Acquisition": set(PLATFORM_NAMES),
    "Expertise et conseil": {"YouTube"},
    "Recrutement": {"Instagram", "TikTok"},
    "Fidélisation": {"Facebook", "Instagram"},
    "Autre": set(),
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
