from config import (
    FORMAT_REQUIRED_SKILLS,
    OBJECTIVE_PRIORITY_PLATFORMS,
    NO_PILOT,
    OUT_OF_SCOPE_NETWORK,
    PERSONA_PLATFORM_REFERENCE,
    PLATFORM_FORMATS,
    PLATFORM_NAMES,
    UNKNOWN_NETWORK,
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


def _known_networks(answers: dict) -> list[str]:
    return [network for network in answers.get("q4", []) if network in PLATFORM_NAMES]


def strategic_control(answers: dict) -> dict:
    blocking: list[str] = []

    if answers.get("q1") != "Oui":
        blocking.append("Finaliser le persona avant de relancer le diagnostic.")

    profiles = list(answers.get("q2", []))
    if len(profiles) != 1:
        blocking.append("Choisir un seul persona pour ce diagnostic.")
    elif profiles[0] == "Autre" and not answers.get("custom_profile", "").strip():
        blocking.append("Préciser le persona à analyser.")

    if not answers.get("priority_need", "").strip():
        blocking.append("Préciser le besoin d’information prioritaire du persona.")

    selected_networks = list(answers.get("q4", []))
    exclusive = {UNKNOWN_NETWORK, OUT_OF_SCOPE_NETWORK}.intersection(selected_networks)
    if not selected_networks:
        blocking.append("Indiquer les réseaux utilisés par le persona ou choisir « Je ne sais pas ».")
    elif exclusive and len(selected_networks) > 1:
        blocking.append("Choisir les réseaux connus ou une seule réponse spéciale.")
    elif OUT_OF_SCOPE_NETWORK in selected_networks:
        blocking.append(
            "CAP compare Facebook, Instagram, TikTok et YouTube. Le réseau indiqué sort du périmètre de l’outil."
        )

    known = _known_networks(answers)
    if known:
        sources = [source for source in answers.get("q5", []) if source != "Aucune source"]
        if not sources:
            blocking.append("Indiquer la source utilisée pour identifier ces réseaux.")
        if answers.get("q5_quality") != "Oui":
            blocking.append(
                "Vérifier que les informations sur les réseaux utilisés sont récentes et fiables."
            )
        preferred = answers.get("q4_priority")
        if len(known) > 1 and preferred not in known + [UNKNOWN_NETWORK]:
            blocking.append(
                "Indiquer le réseau le plus souvent utilisé par le persona ou choisir « Je ne sais pas »."
            )

    objective = answers.get("q6")
    if objective in {None, "", "Non défini"}:
        blocking.append("Définir l’objectif de communication du cabinet.")
    elif objective == "Autre" and not answers.get("custom_objective", "").strip():
        blocking.append("Préciser l’objectif de communication du cabinet.")

    indicator = str(answers.get("indicator", "")).strip()
    target = str(answers.get("target", "")).strip()
    deadline = str(answers.get("deadline", "")).strip()
    if not indicator or not target or not deadline:
        blocking.append("Préciser l’indicateur, le résultat attendu et l’échéance.")
    else:
        if not any(character.isdigit() for character in target):
            blocking.append("Indiquer un résultat attendu chiffré.")
        if not any(character.isdigit() for character in deadline):
            blocking.append("Indiquer une échéance précise.")

    return {
        "status": "Choix validé" if not blocking else "Recommandation impossible",
        "blocking": blocking,
        "review": [],
    }


def _initial_candidates(answers: dict) -> tuple[list[str], str]:
    known = _known_networks(answers)
    if known:
        if len(known) == 1:
            return known, "réseau observé auprès du persona"
        preferred = answers.get("q4_priority")
        if preferred in known:
            return [preferred], "réseau le plus souvent utilisé par le persona"
        return known, "réseaux observés auprès du persona"

    profile = (answers.get("q2") or [None])[0]
    return list(PERSONA_PLATFORM_REFERENCE.get(profile, PLATFORM_NAMES)), "base de référence du persona"


def compare_platforms(answers: dict) -> dict:
    control = strategic_control(answers)
    if control["status"] != "Choix validé":
        return {
            "winner": None,
            "tied_platforms": [],
            "compatible_platforms": [],
            "comparison": {},
            "tie_break": None,
            "outcome": "invalid_data",
            "candidate_basis": None,
        }

    candidates, basis = _initial_candidates(answers)
    objective = answers.get("q6")
    priority_set = OBJECTIVE_PRIORITY_PLATFORMS.get(objective, set())
    priority_candidates = [platform for platform in candidates if platform in priority_set]

    # L'objectif départage seulement s'il laisse au moins une solution. Il ne peut
    # jamais écarter le seul réseau réellement observé auprès du persona.
    finalists = priority_candidates or candidates
    comparison = {
        platform: {
            "persona_or_observed_match": platform in candidates,
            "objective_priority": platform in priority_set,
            "compatible": platform in finalists,
        }
        for platform in PLATFORM_NAMES
    }

    if len(finalists) == 1:
        if len(candidates) == 1:
            tie_break = basis
        else:
            tie_break = "objectif du cabinet"
        return {
            "winner": finalists[0],
            "tied_platforms": [],
            "compatible_platforms": finalists,
            "comparison": comparison,
            "tie_break": tie_break,
            "outcome": "recommended",
            "candidate_basis": basis,
        }

    return {
        "winner": None,
        "tied_platforms": finalists,
        "compatible_platforms": finalists,
        "comparison": comparison,
        "tie_break": "égalité stratégique",
        "outcome": "tie",
        "candidate_basis": basis,
    }


def _criterion(name: str, status: str, observation: str, action: str) -> dict:
    return {
        "criterion": name,
        "status": status,
        "observation": observation,
        "action": action,
    }


def evaluate_feasibility(answers: dict, platform: str | None) -> dict:
    rows: list[dict] = []
    selected_formats = list(answers.get("q14", []))
    supported_formats = (
        [fmt for fmt in selected_formats if fmt in PLATFORM_FORMATS.get(platform, set())]
        if platform
        else selected_formats
    )
    skills = answers.get("q9", {})
    required_skills = required_skills_for_formats(
        supported_formats,
        appears_on_camera=answers.get("q16") == "Oui",
    )

    time = answers.get("q8")
    if time in {None, "", "Aucun temps disponible"}:
        rows.append(_criterion(
            "Temps disponible", "rouge",
            "Aucun temps n’est défini pour produire et suivre les contenus.",
            "Définir et dégager un temps régulier avant de commencer.",
        ))
    elif time == "Moins de 2 h":
        rows.append(_criterion(
            "Temps disponible", "orange",
            "Le temps disponible impose un rythme de publication limité.",
            "Définir un rythme réaliste et l’inscrire dans le plan de charge.",
        ))
    else:
        rows.append(_criterion(
            "Temps disponible", "vert",
            "Un temps mensuel est prévu pour la communication.",
            "Maintenir ce temps dans le plan de charge.",
        ))

    if not selected_formats:
        rows.append(_criterion(
            "Formats et compétences", "rouge",
            "Aucun format régulier n’a été choisi.",
            "Choisir au moins un format que le cabinet peut produire régulièrement.",
        ))
    elif platform and not supported_formats:
        rows.append(_criterion(
            "Formats et compétences", "rouge",
            f"Les formats choisis ne sont pas adaptés à {platform}.",
            "Choisir un format utilisable sur cette plateforme.",
        ))
    else:
        missing = sorted(
            skill for skill in required_skills
            if skills.get(skill, "À acquérir") == "À acquérir"
        )
        partial = sorted(
            skill for skill in required_skills
            if skills.get(skill) == "Notions"
        )
        support = list(answers.get("q12", []))
        confirmations = answers.get("q12_confirmed", {})
        confirmed_support = [item for item in support if confirmations.get(item) == "Oui"]
        if missing and not confirmed_support:
            rows.append(_criterion(
                "Formats et compétences", "rouge",
                f"Compétences à acquérir : {', '.join(missing)}.",
                "Planifier une autoformation, une formation, un appui interne ou un prestataire.",
            ))
        elif missing:
            rows.append(_criterion(
                "Formats et compétences", "orange",
                f"Compétences à acquérir : {', '.join(missing)}.",
                "Mettre en œuvre la solution prévue avant de commencer.",
            ))
        elif partial:
            rows.append(_criterion(
                "Formats et compétences", "orange",
                f"Compétences à renforcer : {', '.join(partial)}.",
                "Préparer un premier contenu et vérifier le temps réellement nécessaire.",
            ))
        else:
            rows.append(_criterion(
                "Formats et compétences", "vert",
                "Les compétences nécessaires aux formats choisis sont maîtrisées.",
                "Aucune action nécessaire.",
            ))

    equipment = set(answers.get("q10", []))
    needs_capture = bool(set(supported_formats).intersection(VIDEO_FORMATS | VISUAL_FORMATS))
    has_capture = bool(equipment.intersection({"Smartphone récent", "Caméra", "Studio équipé"}))
    has_device = bool(equipment.intersection({"Smartphone récent", "Caméra", "Ordinateur", "Studio équipé"}))
    if "Aucun matériel" in equipment or not has_device or (needs_capture and not has_capture):
        rows.append(_criterion(
            "Matériel", "rouge",
            "Le matériel disponible ne permet pas encore de produire les formats choisis.",
            "Prévoir au minimum un smartphone ou le matériel adapté au format retenu.",
        ))
    elif "Connexion internet stable" not in equipment:
        rows.append(_criterion(
            "Matériel", "orange",
            "La connexion utilisée pour publier et répondre reste à vérifier.",
            "Tester la connexion avant la première publication.",
        ))
    else:
        rows.append(_criterion(
            "Matériel", "vert",
            "Le matériel nécessaire est disponible.",
            "Aucune action nécessaire.",
        ))

    pilots = answers.get("q11", [])
    if isinstance(pilots, str):
        pilots = [pilots] if pilots else []
    active_pilots = [pilot for pilot in pilots if pilot != NO_PILOT]
    if not active_pilots:
        rows.append(_criterion(
            "Responsable", "rouge",
            "Aucun responsable n’est encore désigné.",
            "Désigner la personne qui préparera, validera, publiera et suivra les contenus.",
        ))
    else:
        rows.append(_criterion(
            "Responsable", "vert",
            f"Le pilotage est confié à : {', '.join(active_pilots)}.",
            "Préciser les tâches et le temps prévu.",
        ))

    has_cost = answers.get("q13_has_cost")
    budget_validated = answers.get("q13_budget_validated")
    if has_cost not in {"Oui", "Non"}:
        rows.append(_criterion(
            "Budget", "rouge",
            "L’existence d’une dépense n’a pas été vérifiée.",
            "Identifier les dépenses éventuelles et valider leur financement.",
        ))
    elif has_cost == "Oui" and budget_validated != "Oui":
        rows.append(_criterion(
            "Budget", "rouge",
            "Une dépense est prévue, mais son financement n’est pas validé.",
            "Valider le budget ou choisir une solution moins coûteuse.",
        ))
    else:
        rows.append(_criterion(
            "Budget", "vert",
            "Aucune dépense n’est prévue ou le budget nécessaire est validé.",
            "Aucune action nécessaire.",
        ))

    worst = max((STATUS_ORDER[row["status"]] for row in rows), default=1)
    label = {0: "Projet prêt", 1: "Lancement à préparer", 2: "Lancement à reporter"}[worst]
    actions = [row["action"] for row in rows if row["status"] in {"orange", "rouge"}]
    rank = (
        worst,
        sum(row["status"] == "rouge" for row in rows),
        sum(row["status"] == "orange" for row in rows),
    )
    return {"label": label, "rows": rows, "actions": actions, "rank": rank}


def _selection_reasons(answers: dict, platforms: list[str], selection: dict) -> list[str]:
    if not platforms:
        return []
    platform_text = " et ".join(platforms)
    basis = selection.get("candidate_basis")
    if basis == "réseau le plus souvent utilisé par le persona":
        return [
            f"{platform_text} est le réseau que le persona utilise le plus souvent pour rechercher cette information."
        ]
    if basis == "réseau observé auprès du persona" and len(platforms) == 1:
        return [
            f"{platform_text} est le réseau observé auprès du persona pour rechercher cette information."
        ]
    objective = answers.get("q6")
    if objective == "Autre":
        return [
            f"{platform_text} ressort de la base de référence du persona ou des réseaux réellement observés."
        ]
    return [
        f"{platform_text} présente la meilleure cohérence entre le persona, les réseaux connus et l’objectif « {objective} »."
    ]


def evaluate(answers: dict) -> dict:
    control = strategic_control(answers)
    selection = compare_platforms(answers)
    if control["status"] != "Choix validé":
        empty_feasibility = evaluate_feasibility(answers, None)
        return {
            "strategic_status": control["status"],
            "blocking_reason": " ".join(control["blocking"]) or None,
            "decision_notes": control["blocking"],
            "winner": None,
            "tied_platforms": [],
            "recommended_platforms": [],
            "retained_platform": None,
            "compatible_platforms": [],
            "selection_outcome": "invalid_data",
            "comparison": {},
            "tie_break": None,
            "selection_reasons": [],
            "feasibility_label": empty_feasibility["label"],
            "feasibility_rows": empty_feasibility["rows"],
            "launch_actions": empty_feasibility["actions"],
            "alerts": control["blocking"],
        }

    winner = selection["winner"]
    tied = list(selection["tied_platforms"])
    feasibility_by_platform: dict[str, dict] = {}

    if tied:
        feasibility_by_platform = {
            platform: evaluate_feasibility(answers, platform) for platform in tied
        }
        best_rank = min(item["rank"] for item in feasibility_by_platform.values())
        best = [
            platform for platform, item in feasibility_by_platform.items()
            if item["rank"] == best_rank
        ]
        if len(best) == 1:
            winner = best[0]
            tied = []
            selection_outcome = "recommended"
            tie_break = "moyens du cabinet"
        else:
            tied = best
            selection_outcome = "tie"
            tie_break = "égalité reconnue"
    else:
        selection_outcome = selection["outcome"]
        tie_break = selection["tie_break"]

    recommended = [winner] if winner else tied
    retained = answers.get("q15")
    if len(recommended) <= 1 or retained not in recommended:
        retained = None
    platform_for_launch = retained or winner or (tied[0] if tied else None)
    feasibility = (
        feasibility_by_platform.get(platform_for_launch)
        or evaluate_feasibility(answers, platform_for_launch)
    )

    return {
        "strategic_status": "Choix validé",
        "blocking_reason": None,
        "decision_notes": [],
        "winner": winner,
        "tied_platforms": tied,
        "recommended_platforms": recommended,
        "retained_platform": retained,
        "compatible_platforms": selection["compatible_platforms"],
        "selection_outcome": selection_outcome,
        "comparison": selection["comparison"],
        "tie_break": tie_break,
        "selection_reasons": _selection_reasons(answers, recommended, selection),
        "feasibility_label": feasibility["label"],
        "feasibility_rows": feasibility["rows"],
        "launch_actions": feasibility["actions"],
        "feasibility_by_platform": feasibility_by_platform,
        "alerts": feasibility["actions"],
    }
