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
            "Réaliser un diagnostic distinct pour les personas qui ne partagent "
            "pas le même besoin et les mêmes canaux d’information."
        )
    elif answers.get("q2_coherence") == "Partiellement":
        review.append(
            "Vérifier que les profils peuvent réellement être analysés ensemble."
        )

    eligible = [
        network for network in answers.get("q4", []) if network in PLATFORM_NAMES
    ]
    if not eligible:
        blocking.append(
            "Identifier au moins un réseau sur lequel la cible recherche cette "
            "information."
        )

    discovery_modes = [
        mode
        for mode in answers.get("q4_modes", [])
        if mode not in {"Non identifié", "Plusieurs usages"}
    ]
    if not discovery_modes and "Plusieurs usages" not in answers.get("q4_modes", []):
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
    if "Plusieurs usages" in selected_modes:
        selected_modes = set().union(
            *(
                PLATFORM_REFERENCE[name]["discovery_modes"]
                for name in answers.get("q4", [])
                if name in PLATFORM_REFERENCE
            )
        )
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

    if control["status"] == "Recommandation impossible" or not eligible:
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
    elif time in {"Non évalué", "Moins de 2 h"}:
        rows.append(
            _criterion(
                "Temps disponible",
                "orange",
                "Le temps est insuffisamment établi pour confirmer le rythme.",
                "Mesurer la charge et adapter le rythme de publication.",
            )
        )
    else:
        rows.append(
            _criterion(
                "Temps disponible",
                "vert",
                "Une disponibilité mensuelle a été définie.",
                "Inscrire ce temps dans le plan de charge.",
            )
        )

    if platform and not formats:
        rows.append(
            _criterion(
                "Formats et compétences",
                "orange",
                f"Aucun format propre à {platform} n’a été retenu.",
                "Choisir au moins un format régulier avant le lancement.",
            )
        )
    else:
        missing = {
            skill
            for skill in required_skills
            if skills.get(skill, "À acquérir") == "À acquérir"
        }
        partial = {
            skill
            for skill in required_skills
            if skills.get(skill) == "Notions"
        }
        support_status = answers.get("q12_status", "Non évalué")
        if missing and support_status in {
            "Aide indispensable sans solution",
            "Aucune aide nécessaire",
            "Non évalué",
        }:
            rows.append(
                _criterion(
                    "Formats et compétences",
                    "rouge",
                    "Une compétence indispensable manque sans solution organisée.",
                    "Prévoir une formation, un appui ou un prestataire avant de commencer.",
                )
            )
        elif missing or partial:
            rows.append(
                _criterion(
                    "Formats et compétences",
                    "orange",
                    "Certaines compétences doivent encore être consolidées.",
                    "Produire un contenu d’essai et organiser l’aide nécessaire.",
                )
            )
        else:
            rows.append(
                _criterion(
                    "Formats et compétences",
                    "vert",
                    "Les compétences utiles aux formats choisis sont disponibles.",
                    "Formaliser la méthode de production retenue.",
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
                "Préparer un espace de stockage et les accès utiles.",
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
                "Préciser les tâches de préparation, validation, publication et réponse.",
            )
        )

    support_status = answers.get("q12_status", "Non évalué")
    if support_status == "Aide indispensable sans solution":
        rows.append(
            _criterion(
                "Aide prévue",
                "rouge",
                "Une aide est indispensable, mais aucune solution n’a été recherchée.",
                "Trouver un accompagnement avant de commencer.",
            )
        )
    elif support_status in {
        "Aide envisagée mais non organisée",
        "Non évalué",
    }:
        rows.append(
            _criterion(
                "Aide prévue",
                "orange",
                "L’aide nécessaire n’est pas encore organisée.",
                "Choisir la formation ou la personne qui accompagnera le cabinet.",
            )
        )
    else:
        rows.append(
            _criterion(
                "Aide prévue",
                "vert",
                "Le cabinet est autonome ou dispose déjà de l’aide nécessaire.",
                "Conserver les coordonnées et modalités de cet appui.",
            )
        )

    budget = answers.get("q13", "Non évalué")
    if budget == "Dépense indispensable non finançable":
        rows.append(
            _criterion(
                "Budget nécessaire",
                "rouge",
                "Une dépense indispensable ne peut pas être financée.",
                "Choisir une solution moins coûteuse ou reporter le lancement.",
            )
        )
    elif budget in {"Montant à confirmer", "Non évalué"}:
        rows.append(
            _criterion(
                "Budget nécessaire",
                "orange",
                "Une dépense est envisagée, mais son montant reste à confirmer.",
                "Chiffrer et valider le coût avant le lancement.",
            )
        )
    else:
        rows.append(
            _criterion(
                "Budget nécessaire",
                "vert",
                "Aucune dépense n’est nécessaire ou le budget couvre les besoins.",
                "Suivre les dépenses réellement engagées.",
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
    winner = selection["winner"]
    observation_platform = answers.get("q15")
    if observation_platform not in selection["tied_platforms"]:
        observation_platform = None
    platform_for_launch = winner or observation_platform
    feasibility = evaluate_feasibility(answers, platform_for_launch)

    if control["status"] == "Recommandation impossible":
        winner = None
        platform_for_launch = None

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
