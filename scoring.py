from config import (
    FORMAT_REQUIRED_SKILLS,
    PLATFORM_NAMES,
    PLATFORM_REFERENCE,
    VIDEO_FORMATS,
    VISUAL_FORMATS,
)


STATUS_ORDER = {"vert": 0, "orange": 1, "rouge": 2}


def required_skills_for_formats(formats: list[str]) -> set[str]:
    required: set[str] = set()
    for content_format in formats:
        required.update(FORMAT_REQUIRED_SKILLS.get(content_format, set()))
    return required


def strategic_control(answers: dict) -> dict:
    blocking = []
    review = []

    if answers.get("q1") == "Non":
        blocking.append("Finaliser le persona de la clientèle recherchée.")
    elif answers.get("q1") == "Partiellement":
        review.append("Finaliser les informations encore partielles du persona.")

    profiles = [
        profile
        for profile in answers.get("q2", [])
        if profile != "Non identifié"
    ]
    if not profiles:
        blocking.append("Identifier au moins un profil cible.")

    if answers.get("q3") == "Non" or not answers.get("priority_need", "").strip():
        blocking.append(
            "Définir le besoin prioritaire auquel le cabinet souhaite répondre."
        )
    elif answers.get("q3") == "Partiellement":
        review.append("Compléter le recensement des besoins de la cible.")

    if answers.get("q2_coherence") == "Non":
        blocking.append(
            "Conserver uniquement les profils qui recherchent la même information "
            "sur les mêmes réseaux, puis réaliser un diagnostic séparé pour les autres."
        )
    elif answers.get("q2_coherence") in {"À vérifier", "Partiellement"}:
        review.append(
            "Confirmer que les profils sélectionnés recherchent la même information "
            "sur les mêmes réseaux."
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
        *(
            reference["discovery_modes"]
            for reference in PLATFORM_REFERENCE.values()
        )
    )
    discovery_modes = [
        mode
        for mode in answers.get("q4_modes", [])
        if mode in known_discovery_modes
    ]
    if not discovery_modes:
        blocking.append(
            "Préciser comment la cible accède habituellement à cette information."
        )

    sources = [
        source for source in answers.get("q5", []) if source != "Aucune source"
    ]
    if not sources:
        blocking.append(
            "Documenter le comportement de la cible à partir d’au moins une source."
        )
    elif len(sources) == 1:
        review.append("Recouper l’information avec une seconde source.")

    quality = answers.get("q5_quality")
    if quality == "Anciennes ou non vérifiées":
        blocking.append(
            "Actualiser et vérifier les informations relatives aux canaux de la cible."
        )
    elif quality == "Partiellement vérifiées":
        review.append("Recouper les informations encore partiellement vérifiées.")

    if answers.get("q6") in {None, "", "Non défini"}:
        blocking.append("Définir l’objectif poursuivi par le cabinet.")
    if not all(
        str(answers.get(field, "")).strip()
        for field in ("indicator", "target", "deadline")
    ):
        blocking.append(
            "Préciser l’indicateur, le résultat attendu et l’échéance de l’objectif."
        )
    if answers.get("q6_treatment") in {None, "", "Non défini"}:
        blocking.append("Choisir le traitement éditorial adapté au projet.")
    if answers.get("q6_effect") in {None, "", "Non défini"}:
        blocking.append("Préciser l’effet principal recherché auprès de l’audience.")

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


def _platform_correspondences(answers: dict, platform: str) -> list[str]:
    reference = PLATFORM_REFERENCE[platform]
    correspondences = []
    if answers.get("q6") in reference["objectives"]:
        correspondences.append("objectif")

    selected_modes = set(answers.get("q4_modes", []))
    if selected_modes.intersection(reference["discovery_modes"]):
        correspondences.append("mode de découverte")
    if answers.get("q6_treatment") == reference["editorial_treatment"]:
        correspondences.append("traitement éditorial")
    if answers.get("q6_effect") == reference["audience_effect"]:
        correspondences.append("effet recherché")
    return correspondences


def compare_platforms(answers: dict) -> dict:
    control = strategic_control(answers)
    eligible = [
        network for network in answers.get("q4", []) if network in PLATFORM_NAMES
    ]
    comparison = {
        platform: _platform_correspondences(answers, platform)
        for platform in eligible
    }

    if control["status"] != "Choix validé" or not eligible:
        return {
            "winner": None,
            "tied_platforms": [],
            "comparison": comparison,
            "tie_break": None,
        }

    best_count = max(len(items) for items in comparison.values())
    tied = [
        platform
        for platform, items in comparison.items()
        if len(items) == best_count
    ]
    if len(tied) == 1:
        return {
            "winner": tied[0],
            "tied_platforms": [],
            "comparison": comparison,
            "tie_break": "caractéristiques de la plateforme",
        }

    statuses = answers.get("q7", {})
    result_rank = {
        platform: {
            "Contacts obtenus": 2,
            "Audience cible engagée": 1,
        }.get(statuses.get(platform, "Aucun compte"), 0)
        for platform in tied
    }
    highest_result = max(result_rank.values(), default=0)
    result_leaders = [
        platform
        for platform in tied
        if result_rank[platform] == highest_result
    ]
    if highest_result > 0 and len(result_leaders) == 1:
        return {
            "winner": result_leaders[0],
            "tied_platforms": [],
            "comparison": comparison,
            "tie_break": "résultats déjà obtenus auprès de la cible",
        }

    # Le compte actif n’intervient qu’en l’absence de résultat qualifié.
    if highest_result == 0:
        active_rank = {
            platform: int(statuses.get(platform) == "Compte actif")
            for platform in tied
        }
        active_leaders = [
            platform
            for platform in tied
            if active_rank[platform] == max(active_rank.values(), default=0)
        ]
        if max(active_rank.values(), default=0) > 0 and len(active_leaders) == 1:
            return {
                "winner": active_leaders[0],
                "tied_platforms": [],
                "comparison": comparison,
                "tie_break": "compte déjà actif",
            }

    return {
        "winner": None,
        "tied_platforms": tied,
        "comparison": comparison,
        "tie_break": "égalité reconnue",
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
    required_skills = required_skills_for_formats(formats)

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


def build_selection_reasons(platform: str | None, comparison: dict) -> list[str]:
    if not platform:
        return []
    reference = PLATFORM_REFERENCE[platform]
    reasons = []
    matched = comparison.get(platform, [])
    if "objectif" in matched:
        reasons.append("La plateforme peut contribuer à l’objectif retenu.")
    if "mode de découverte" in matched:
        reasons.append(
            f"Son mode d’accès dominant repose sur {reference['discovery_label']}."
        )
    if "traitement éditorial" in matched:
        reasons.append(
            f"Le traitement attendu correspond à {reference['treatment_label']}."
        )
    if "effet recherché" in matched:
        reasons.append(
            f"L’effet recherché est la {reference['effect_label']}."
        )
    return reasons


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
        "observation_platform": observation_platform,
        "platform_for_launch": platform_for_launch,
        "comparison": selection["comparison"],
        "tie_break": selection["tie_break"],
        "selection_reasons": build_selection_reasons(
            winner, selection["comparison"]
        ),
        "feasibility_label": feasibility["label"],
        "feasibility_rows": feasibility["rows"],
        "launch_actions": feasibility["actions"],
        # Alias conservé pour l’export et les intégrations antérieures.
        "alerts": control["blocking"] + control["review"] + feasibility["actions"],
    }
