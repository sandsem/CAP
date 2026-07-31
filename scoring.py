from config import (
    FORMAT_REQUIRED_SKILLS,
    PLATFORM_NAMES,
    PLATFORM_REFERENCE,
    VIDEO_FORMATS,
    VISUAL_FORMATS,
)


STATUS_ORDER = {"vert": 0, "orange": 1, "rouge": 2}


def required_skills_for_formats(
    formats: list[str],
    appears_on_camera: bool = False,
) -> set[str]:
    required: set[str] = set()
    for content_format in formats:
        required.update(FORMAT_REQUIRED_SKILLS.get(content_format, set()))
    if appears_on_camera and set(formats).intersection(VIDEO_FORMATS):
        required.add("Aisance face caméra")
    return required


def strategic_control(answers: dict) -> dict:
    blocking = []
    review = []

    if answers.get("q1") != "Oui":
        blocking.append("Finaliser le persona de la clientèle recherchée.")

    profiles = [
        profile
        for profile in answers.get("q2", [])
        if profile != "Non identifié"
    ]
    if not profiles:
        blocking.append("Identifier le persona à analyser.")
    elif len(profiles) > 1:
        blocking.append(
            "Conserver un seul persona et réaliser un diagnostic séparé pour les autres."
        )

    if (
        answers.get("q3") in {"Non", "Partiellement"}
        or not answers.get("priority_need", "").strip()
    ):
        blocking.append(
            "Définir le besoin d’information prioritaire du persona."
        )

    eligible = [
        network for network in answers.get("q4", []) if network in PLATFORM_NAMES
    ]
    if not eligible:
        blocking.append(
            "Identifier au moins un réseau sur lequel la cible recherche cette "
            "information."
        )

    known_discovery_modes = set().union(
        *(reference["discovery_modes"] for reference in PLATFORM_REFERENCE.values())
    )
    modes_by_network = answers.get("q4_modes_by_network", {})
    missing_modes = [
        platform
        for platform in eligible
        if modes_by_network.get(platform) not in known_discovery_modes
    ]
    if missing_modes:
        blocking.append(
            "Préciser comment le persona recherche cette information sur "
            f"{', '.join(missing_modes)}."
        )

    sources = [
        source for source in answers.get("q5", []) if source != "Aucune source"
    ]
    if not sources:
        blocking.append(
            "Documenter le comportement de la cible à partir d’au moins une source."
        )

    quality = answers.get("q5_quality")
    if quality == "Anciennes ou non vérifiées":
        blocking.append(
            "Actualiser et vérifier les informations relatives aux canaux de la cible."
        )
    elif quality == "Partiellement vérifiées":
        review.append(
            "Confirmer les réseaux utilisés par le persona à l’aide d’une source récente."
        )

    objective = answers.get("q6")
    if objective in {None, "", "Non défini"}:
        blocking.append("Définir l’objectif poursuivi par le cabinet.")
    elif objective == "Autre":
        blocking.append(
            "Choisir un objectif proposé afin de pouvoir comparer les plateformes."
        )

    indicator = str(answers.get("indicator", "")).strip()
    target = str(answers.get("target", "")).strip()
    deadline = str(answers.get("deadline", "")).strip()
    if not indicator or not target or not deadline:
        blocking.append(
            "Préciser l’indicateur, le résultat attendu et l’échéance de l’objectif."
        )
    else:
        if not any(character.isdigit() for character in target):
            blocking.append("Indiquer un résultat attendu chiffré.")
        if not any(character.isdigit() for character in deadline):
            blocking.append("Indiquer une échéance précise.")

    if blocking:
        return {
            "status": "Recommandation impossible",
            "blocking": blocking,
            "review": review,
        }
    if review:
        return {
            "status": "Projet à revoir",
            "blocking": [],
            "review": review,
        }
    return {"status": "Choix validé", "blocking": [], "review": []}


def _platform_checks(answers: dict, platform: str) -> dict:
    reference = PLATFORM_REFERENCE[platform]
    mode = answers.get("q4_modes_by_network", {}).get(platform)
    objective_match = answers.get("q6") in reference["objectives"]
    usage_match = mode in reference["discovery_modes"]
    return {
        "objective_match": objective_match,
        "usage_match": usage_match,
        "compatible": objective_match and usage_match,
    }


def compare_platforms(answers: dict) -> dict:
    control = strategic_control(answers)
    eligible = [
        network for network in answers.get("q4", []) if network in PLATFORM_NAMES
    ]
    comparison = {platform: _platform_checks(answers, platform) for platform in eligible}
    compatible = [
        platform
        for platform in eligible
        if comparison[platform]["compatible"]
    ]

    if control["status"] != "Choix validé" or not eligible:
        return {
            "winner": None,
            "tied_platforms": [],
            "compatible_platforms": compatible,
            "comparison": comparison,
            "tie_break": None,
            "outcome": "invalid_data",
        }

    if not compatible:
        return {
            "winner": None,
            "tied_platforms": [],
            "compatible_platforms": [],
            "comparison": comparison,
            "tie_break": None,
            "outcome": "no_compatible_platform",
        }

    if len(compatible) == 1:
        return {
            "winner": compatible[0],
            "tied_platforms": [],
            "compatible_platforms": compatible,
            "comparison": comparison,
            "tie_break": "objectif et usage du persona",
            "outcome": "recommended",
        }

    statuses = answers.get("q7", {})
    result_leaders = [
        platform
        for platform in compatible
        if statuses.get(platform) in {"Audience cible engagée", "Contacts obtenus"}
    ]
    if len(result_leaders) == 1:
        return {
            "winner": result_leaders[0],
            "tied_platforms": [],
            "compatible_platforms": compatible,
            "comparison": comparison,
            "tie_break": "résultat déjà obtenu auprès de ce persona",
            "outcome": "recommended",
        }
    if len(result_leaders) > 1:
        return {
            "winner": None,
            "tied_platforms": result_leaders,
            "compatible_platforms": compatible,
            "comparison": comparison,
            "tie_break": "égalité reconnue",
            "outcome": "tie",
        }

    return {
        "winner": None,
        "tied_platforms": compatible,
        "compatible_platforms": compatible,
        "comparison": comparison,
        "tie_break": "égalité reconnue",
        "outcome": "tie",
    }


def _criterion(name: str, status: str, observation: str, action: str) -> dict:
    return {
        "criterion": name,
        "status": status,
        "observation": observation,
        "action": action,
    }


def evaluate_feasibility(answers: dict, platform: str | None) -> dict:
    rows = []
    formats = list(answers.get("q14", []))
    skills = answers.get("q9", {})
    required_skills = required_skills_for_formats(
        formats,
        appears_on_camera=answers.get("q16") == "Oui",
    )

    time = answers.get("q8", "Non évalué")
    if time == "Aucun temps disponible":
        rows.append(
            _criterion(
                "Temps disponible",
                "rouge",
                "Aucun temps ne peut être consacré au projet.",
                "Reporter le lancement ou dégager une disponibilité réelle.",
            )
        )
    elif time == "Non évalué":
        rows.append(
            _criterion(
                "Temps disponible",
                "orange",
                "Le temps disponible n’a pas été évalué.",
                "Évaluer le temps mensuel disponible avant de commencer.",
            )
        )
    elif time == "Moins de 2 h":
        rows.append(
            _criterion(
                "Temps disponible",
                "orange",
                "Moins de deux heures par mois risque de ne pas suffire.",
                "Réduire le rythme de publication ou dégager davantage de temps.",
            )
        )
    else:
        rows.append(
            _criterion(
                "Temps disponible",
                "vert",
                "Le temps mensuel consacré au projet est défini.",
                "Aucune action nécessaire.",
            )
        )

    if not formats:
        rows.append(
            _criterion(
                "Formats et compétences",
                "orange",
                "Aucun format régulier n’a été retenu.",
                "Choisir au moins un format régulier avant le lancement.",
            )
        )
    else:
        missing = sorted(
            skill
            for skill in required_skills
            if skills.get(skill, "À acquérir") == "À acquérir"
        )
        partial = sorted(
            skill
            for skill in required_skills
            if skills.get(skill) == "Notions"
        )
        support = set(answers.get("q12", []))
        legacy_support = {
            "Appui interne": "Aide interne",
            "Prestataire externe": "Prestataire",
        }
        support = {legacy_support.get(item, item) for item in support}
        concrete_support = bool(
            support.intersection(
                {
                    "Autoformation",
                    "Formation",
                    "Aide interne",
                    "Prestataire",
                    "Autre solution",
                }
            )
        )
        if missing and not concrete_support:
            rows.append(
                _criterion(
                    "Formats et compétences",
                    "rouge",
                    f"Compétences à acquérir : {', '.join(missing)}.",
                    "Choisir une autoformation, une formation, une aide interne "
                    "ou un prestataire.",
                )
            )
        elif missing:
            rows.append(
                _criterion(
                    "Formats et compétences",
                    "orange",
                    f"Compétences à acquérir : {', '.join(missing)}.",
                    "Mettre en œuvre la solution retenue avant de commencer.",
                )
            )
        elif partial:
            rows.append(
                _criterion(
                    "Formats et compétences",
                    "orange",
                    f"Compétences à renforcer : {', '.join(partial)}.",
                    "Mettre en œuvre la solution retenue et réaliser un contenu d’essai.",
                )
            )
        else:
            rows.append(
                _criterion(
                    "Formats et compétences",
                    "vert",
                    "Les compétences nécessaires sont maîtrisées.",
                    "Aucune action nécessaire.",
                )
            )

    equipment = set(answers.get("q10", []))
    selected = set(formats)
    lacks_capture = not equipment.intersection({"Smartphone récent", "Caméra"})
    lacks_workstation = "Ordinateur" not in equipment
    if "Aucun matériel" in equipment or (
        selected.intersection(VIDEO_FORMATS) and lacks_capture
    ) or (
        selected.intersection(VISUAL_FORMATS) and lacks_capture and lacks_workstation
    ):
        rows.append(
            _criterion(
                "Matériel",
                "rouge",
                "Le matériel indispensable aux formats retenus n’est pas disponible.",
                "Acquérir, emprunter ou louer le matériel avant le lancement.",
            )
        )
    elif "Connexion stable" not in equipment:
        rows.append(
            _criterion(
                "Matériel",
                "orange",
                "La connexion nécessaire à la publication et au suivi reste à vérifier.",
                "Tester la connexion et les outils avant la première publication.",
            )
        )
    else:
        rows.append(
            _criterion(
                "Matériel",
                "vert",
                "Le matériel nécessaire est disponible.",
                "Aucune action nécessaire.",
            )
        )

    if answers.get("q11") in {None, "", "Non défini"}:
        rows.append(
            _criterion(
                "Responsable",
                "rouge",
                "Personne ne peut encore prendre en charge le projet.",
                "Désigner un responsable et définir ses tâches avant le lancement.",
            )
        )
    else:
        rows.append(
            _criterion(
                "Responsable",
                "vert",
                "Le pilotage du projet est attribué.",
                "Aucune action nécessaire.",
            )
        )

    legacy_budget = {
        "Budget validé": "Oui",
        "Montant à confirmer": "À vérifier",
        "Dépense indispensable non finançable": "Non",
        "Non évalué": "À vérifier",
    }
    budget = legacy_budget.get(answers.get("q13"), answers.get("q13", "À vérifier"))
    if budget == "Non":
        rows.append(
            _criterion(
                "Budget",
                "rouge",
                "Une dépense indispensable ne peut pas être financée.",
                "Choisir une solution moins coûteuse ou reporter le lancement.",
            )
        )
    elif budget == "À vérifier":
        rows.append(
            _criterion(
                "Budget",
                "orange",
                "Le coût nécessaire au lancement reste à vérifier.",
                "Chiffrer les dépenses avant de commencer.",
            )
        )
    else:
        rows.append(
            _criterion(
                "Budget",
                "vert",
                "Aucune dépense n’est nécessaire ou le cabinet peut la financer.",
                "Aucune action nécessaire.",
            )
        )

    worst = max((STATUS_ORDER[row["status"]] for row in rows), default=1)
    if worst == STATUS_ORDER["rouge"]:
        label = "Lancement à reporter"
    elif worst == STATUS_ORDER["orange"]:
        label = "Lancement à préparer"
    else:
        label = "Projet prêt"

    actions = [
        row["action"]
        for row in rows
        if row["status"] in {"orange", "rouge"}
    ]
    return {"label": label, "rows": rows, "actions": actions}


def build_selection_reasons(
    platform: str | None,
    comparison: dict,
    objective: str | None,
) -> list[str]:
    if not platform:
        return []
    checks = comparison.get(platform, {})
    if not checks.get("compatible"):
        return []
    return [
        f"Parmi les réseaux utilisés par ce persona pour rechercher cette "
        f"information, {platform} correspond à la fois à son mode d’accès et "
        f"à l’objectif « {objective} » du cabinet."
    ]


def evaluate(answers: dict) -> dict:
    control = strategic_control(answers)
    selection = compare_platforms(answers)
    strategic_choice_is_valid = control["status"] == "Choix validé"
    winner = selection["winner"] if strategic_choice_is_valid else None
    observation_platform = answers.get("q15")
    if (
        not strategic_choice_is_valid
        or observation_platform not in selection["tied_platforms"]
    ):
        observation_platform = None
    platform_for_launch = winner or observation_platform
    feasibility = evaluate_feasibility(answers, platform_for_launch)

    return {
        "strategic_status": control["status"],
        "blocking_reason": " ".join(control["blocking"]) or None,
        "decision_notes": control["blocking"] + control["review"],
        "winner": winner,
        "tied_platforms": selection["tied_platforms"],
        "compatible_platforms": selection["compatible_platforms"],
        "selection_outcome": selection["outcome"],
        "observation_platform": observation_platform,
        "platform_for_launch": platform_for_launch,
        "comparison": selection["comparison"],
        "tie_break": selection["tie_break"],
        "selection_reasons": build_selection_reasons(
            winner,
            selection["comparison"],
            answers.get("q6"),
        ),
        "feasibility_label": feasibility["label"],
        "feasibility_rows": feasibility["rows"],
        "launch_actions": feasibility["actions"],
        # Alias conservé pour l’export et les intégrations antérieures.
        "alerts": control["blocking"] + control["review"] + feasibility["actions"],
    }
