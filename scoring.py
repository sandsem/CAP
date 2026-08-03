from __future__ import annotations

from config import (
    CONTENT_REUSE_PAIRS,
    FORMAT_REQUIRED_SKILLS,
    INDICATOR_OPTIONS,
    INDICATORS_BY_OBJECTIVE,
    NEED_CATEGORY_KEYWORDS,
    NEED_PLATFORM_PRIORITY,
    NO_PILOT,
    OBJECTIVE_PRIORITY_PLATFORMS,
    OUT_OF_SCOPE_NETWORK,
    PERSONA_PLATFORM_REFERENCE,
    PLATFORM_ESSENTIAL_FORMATS,
    PLATFORM_FORMATS,
    PLATFORM_NAMES,
    PLATFORM_ROLES,
    UNKNOWN_NETWORK,
    VIDEO_FORMATS,
    VISUAL_FORMATS,
)


STATUS_ORDER = {"vert": 0, "orange": 1, "rouge": 2}
TIME_ORDER = {
    "Aucun temps disponible": 0,
    "Moins de 2 h": 1,
    "2 à 5 h": 2,
    "6 à 10 h": 3,
    "Plus de 10 h": 4,
}
EXTERNAL_SIGNAL_ORDER = {"fort": 3, "modéré": 2, "faible": 1, "indisponible": 0}


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


def _positive_number(text: str) -> bool:
    numbers = []
    current = ""
    for character in str(text):
        if character.isdigit() or character in {",", "."}:
            current += character
        elif current:
            numbers.append(current)
            current = ""
    if current:
        numbers.append(current)
    for value in numbers:
        try:
            if float(value.replace(",", ".")) > 0:
                return True
        except ValueError:
            continue
    return False


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
        blocking.append("Choisir les réseaux utilisés ou une seule réponse spéciale.")
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
        allowed_indicators = INDICATORS_BY_OBJECTIVE.get(objective, INDICATOR_OPTIONS)
        if indicator in INDICATOR_OPTIONS and indicator not in allowed_indicators:
            blocking.append("Choisir un indicateur directement lié à l’objectif défini.")
        if not _positive_number(target):
            blocking.append("Indiquer un résultat attendu chiffré supérieur à zéro.")
        if not _positive_number(deadline):
            blocking.append("Indiquer une échéance précise et supérieure à zéro.")

    return {
        "status": "Choix validé" if not blocking else "Recommandation impossible",
        "blocking": blocking,
        "review": [],
    }


def classify_need(priority_need: str) -> dict:
    text = (priority_need or "").lower()
    matches: dict[str, int] = {}
    for category, keywords in NEED_CATEGORY_KEYWORDS.items():
        matches[category] = sum(keyword in text for keyword in keywords)
    best_category = max(matches, key=matches.get, default="général")
    if not matches or matches.get(best_category, 0) == 0:
        best_category = "général"
    return {
        "category": best_category,
        "platforms": NEED_PLATFORM_PRIORITY.get(best_category, PLATFORM_NAMES),
        "explanation": {
            "explication approfondie": "Le besoin appelle une explication structurée et durable.",
            "démarche pratique": "Le besoin appelle une méthode, des étapes ou une démonstration.",
            "actualité et échéance": "Le besoin exige une information claire, datée et facilement actualisable.",
            "confiance et réassurance": "Le besoin appelle de la pédagogie et des éléments de réassurance.",
            "recrutement": "Le besoin concerne l’attractivité du cabinet et la présentation de son environnement de travail.",
            "fidélisation": "Le besoin concerne la continuité de la relation avec la clientèle existante.",
            "découverte": "Le besoin vise d’abord à faire connaître le cabinet et ses domaines d’intervention.",
            "général": "Le besoin ne relève pas d’une famille unique ; CAP croise donc l’ensemble des autres critères.",
        }[best_category],
    }


def _need_fit(platform: str, category: str) -> int:
    primary_groups = {
        "explication approfondie": {"YouTube"},
        "démarche pratique": {"YouTube", "Instagram"},
        "actualité et échéance": {"Facebook", "Instagram", "TikTok"},
        "confiance et réassurance": {"YouTube", "Instagram", "Facebook"},
        "recrutement": {"Instagram", "TikTok"},
        "fidélisation": {"Facebook", "Instagram"},
        "découverte": {"Instagram", "TikTok"},
        "général": set(PLATFORM_NAMES),
    }
    secondary_groups = {
        "explication approfondie": {"Instagram", "Facebook"},
        "démarche pratique": {"TikTok", "Facebook"},
        "actualité et échéance": {"YouTube"},
        "confiance et réassurance": {"TikTok"},
        "recrutement": {"Facebook", "YouTube"},
        "fidélisation": {"YouTube", "TikTok"},
        "découverte": {"Facebook", "YouTube"},
        "général": set(),
    }
    if platform in primary_groups.get(category, set()):
        return 2
    if platform in secondary_groups.get(category, set()):
        return 1
    return 0


def _objective_fit(platform: str, objective: str) -> int:
    primary_groups = {
        "Visibilité et notoriété": {"Instagram", "TikTok"},
        "Acquisition": set(PLATFORM_NAMES),
        "Expertise et conseil": {"YouTube"},
        "Recrutement": {"Instagram", "TikTok"},
        "Fidélisation": {"Facebook", "Instagram"},
        "Autre": set(PLATFORM_NAMES),
    }
    secondary_groups = {
        "Visibilité et notoriété": {"Facebook", "YouTube"},
        "Acquisition": set(),
        "Expertise et conseil": {"Instagram", "Facebook"},
        "Recrutement": {"Facebook", "YouTube"},
        "Fidélisation": {"YouTube", "TikTok"},
        "Autre": set(),
    }
    if platform in primary_groups.get(objective, set()):
        return 2
    if platform in secondary_groups.get(objective, set()):
        return 1
    return 0


def _external_signal(external_research: dict | None, platform: str) -> str:
    if not external_research:
        return "indisponible"
    return external_research.get("platforms", {}).get(platform, {}).get("signal", "indisponible")


def _platform_evidence(
    answers: dict,
    platform: str,
    need_analysis: dict,
    external_research: dict | None,
) -> dict:
    known = _known_networks(answers)
    profile = (answers.get("q2") or ["Autre"])[0]
    reference = PERSONA_PLATFORM_REFERENCE.get(profile, PLATFORM_NAMES)
    objective = answers.get("q6")

    target_fit = 2 if platform in known else (1 if platform in reference else 0)
    need_fit = _need_fit(platform, need_analysis["category"])
    objective_fit = _objective_fit(platform, objective)
    external_label = _external_signal(external_research, platform)
    external_rank = EXTERNAL_SIGNAL_ORDER.get(external_label, 0)
    external_match = external_rank >= 2
    core_count = sum((target_fit > 0, need_fit > 0, objective_fit > 0, external_match))

    return {
        "platform": platform,
        "target_fit": target_fit,
        "need_fit": need_fit,
        "objective_fit": objective_fit,
        "core_count": core_count,
        "strategic_depth": need_fit + objective_fit,
        "external_signal": external_label,
        "external_rank": external_rank,
        "external_match": external_match,
        "observed": platform in known,
        "reference": platform in reference,
        "role": PLATFORM_ROLES[platform],
    }


def _criterion(name: str, status: str, observation: str, action: str) -> dict:
    return {
        "criterion": name,
        "status": status,
        "observation": observation,
        "action": action,
    }


def _active_pilots(answers: dict) -> list[str]:
    pilots = answers.get("q11", [])
    if isinstance(pilots, str):
        pilots = [pilots] if pilots else []
    active: list[str] = []
    for pilot in pilots:
        if pilot == NO_PILOT:
            continue
        if pilot == "Autre":
            custom_pilot = str(answers.get("custom_pilot", "")).strip()
            if custom_pilot:
                active.append(custom_pilot)
        else:
            active.append(pilot)
    return active


def evaluate_feasibility(answers: dict, platform: str | None) -> dict:
    rows: list[dict] = []
    selected_formats = list(answers.get("q14", []))
    compatible_formats = (
        [fmt for fmt in selected_formats if fmt in PLATFORM_FORMATS.get(platform, set())]
        if platform
        else selected_formats
    )
    essential_formats = PLATFORM_ESSENTIAL_FORMATS.get(platform, set()) if platform else set()
    selected_essential = sorted(set(compatible_formats).intersection(essential_formats))
    skills = answers.get("q9", {})
    required_skills = required_skills_for_formats(
        compatible_formats,
        appears_on_camera=answers.get("q16") == "Oui",
    )

    time = answers.get("q8")
    if time in {None, "", "Aucun temps disponible"}:
        rows.append(_criterion(
            "Temps disponible", "rouge",
            "Aucun temps n’est défini pour produire, publier et suivre les contenus.",
            "Dégager un temps régulier dans le plan de charge avant de commencer.",
        ))
    elif time == "Moins de 2 h":
        rows.append(_criterion(
            "Temps disponible", "orange",
            "Le temps disponible est très limité pour assurer la préparation, la publication et le suivi.",
            "Réduire le rythme, simplifier les formats et réserver un créneau récurrent avant le lancement.",
        ))
    elif platform == "YouTube" and time == "2 à 5 h":
        rows.append(_criterion(
            "Temps disponible", "orange",
            "Le temps disponible permet un démarrage progressif, mais limite la production de vidéos longues.",
            "Commencer par un format vidéo simple et inscrire sa durée réelle dans le plan de charge.",
        ))
    else:
        rows.append(_criterion(
            "Temps disponible", "vert",
            "Un temps mensuel est prévu pour préparer, publier et suivre les contenus.",
            "Maintenir ce temps dans le plan de charge.",
        ))

    format_status = "vert"
    format_observations: list[str] = []
    format_actions: list[str] = []
    if not selected_formats:
        format_status = "rouge"
        format_observations.append("Aucun format régulier n’a été choisi.")
        format_actions.append("Choisir les formats que le cabinet pourra réellement produire.")
    elif platform and not compatible_formats:
        format_status = "orange"
        format_observations.append(f"Les formats actuellement choisis ne sont pas utilisables sur {platform}.")
        if platform in {"TikTok", "YouTube"}:
            format_actions.append(
                "Se former à une production vidéo simple, y compris sans apparition à l’écran, puis choisir un second format compatible avant le lancement."
            )
        else:
            format_actions.append(
                "Choisir un format structurant et un format complémentaire compatibles avec cette plateforme avant le lancement."
            )
    else:
        if platform and essential_formats and not selected_essential:
            format_status = "orange"
            format_observations.append(
                f"Aucun format structurant de {platform} n’est actuellement retenu."
            )
            if platform in {"TikTok", "YouTube"}:
                format_actions.append(
                    "Se former à une production vidéo simple, y compris sans apparition à l’écran, avant le lancement."
                )
            else:
                format_actions.append(
                    "Ajouter un format structurant adapté à la plateforme avant le lancement."
                )
        if len(set(compatible_formats)) < 2:
            if format_status != "rouge":
                format_status = "orange"
            format_observations.append("La communication repose actuellement sur un seul format compatible.")
            format_actions.append(
                "Prévoir un second format complémentaire afin de diversifier les publications."
            )

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
            format_status = "rouge"
            format_observations.append(f"Compétences à acquérir : {', '.join(missing)}.")
            format_actions.append(
                "Planifier une autoformation, une formation, un appui interne ou un prestataire avant de commencer."
            )
        elif missing:
            if format_status != "rouge":
                format_status = "orange"
            format_observations.append(f"Compétences à acquérir : {', '.join(missing)}.")
            format_actions.append("Mettre en œuvre la solution prévue avant la première publication.")
        elif partial:
            if format_status != "rouge":
                format_status = "orange"
            format_observations.append(f"Compétences à renforcer : {', '.join(partial)}.")
            format_actions.append("Réaliser la formation ou l’entraînement nécessaire avant le lancement.")

        if not format_observations:
            format_observations.append(
                "Un format structurant et un format complémentaire sont réalisables avec les compétences déclarées."
            )
            format_actions.append("Aucune action indispensable avant le lancement.")

    rows.append(_criterion(
        "Formats et compétences",
        format_status,
        " ".join(format_observations),
        " ".join(dict.fromkeys(format_actions)),
    ))

    equipment = set(answers.get("q10", []))
    needs_capture = bool(set(compatible_formats).intersection(VIDEO_FORMATS | VISUAL_FORMATS))
    has_capture = bool(equipment.intersection({"Smartphone récent", "Caméra", "Studio équipé"}))
    has_device = bool(equipment.intersection({"Smartphone récent", "Caméra", "Ordinateur", "Studio équipé"}))
    if "Aucun matériel" in equipment or not has_device or (needs_capture and not has_capture):
        rows.append(_criterion(
            "Matériel", "rouge",
            "Le matériel disponible ne permet pas encore de produire les formats retenus.",
            "Prévoir au minimum un smartphone, un ordinateur ou le matériel adapté au format avant de commencer.",
        ))
    elif "Connexion internet stable" not in equipment:
        rows.append(_criterion(
            "Matériel", "orange",
            "Le matériel de production est disponible, mais la connexion utilisée reste à vérifier.",
            "Tester la connexion avant la première publication.",
        ))
    else:
        rows.append(_criterion(
            "Matériel", "vert",
            "Le matériel nécessaire aux formats retenus est disponible.",
            "Aucune action indispensable avant le lancement.",
        ))

    active_pilots = _active_pilots(answers)
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
            "Préciser les tâches et le temps attribués à chaque personne dans le plan de charge.",
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
            "Valider le budget ou retenir une solution gratuite avant de commencer.",
        ))
    else:
        rows.append(_criterion(
            "Budget", "vert",
            "Aucune dépense n’est prévue ou le budget nécessaire est validé.",
            "Reporter les montants dans le plan de charge pour suivre le coût réel.",
        ))

    worst = max((STATUS_ORDER[row["status"]] for row in rows), default=1)
    label = {0: "Projet prêt", 1: "Lancement à préparer", 2: "Lancement à reporter"}[worst]
    actions = list(dict.fromkeys(
        row["action"] for row in rows if row["status"] in {"orange", "rouge"}
    ))
    rank = (
        worst,
        sum(row["status"] == "rouge" for row in rows),
        sum(row["status"] == "orange" for row in rows),
    )
    return {
        "label": label,
        "rows": rows,
        "actions": actions,
        "rank": rank,
        "compatible_formats": compatible_formats,
        "essential_formats_selected": selected_essential,
        "actors": active_pilots,
    }


def _choose_winner(
    answers: dict,
    evidence: dict[str, dict],
    feasibility: dict[str, dict],
) -> tuple[str, str, list[str]]:
    # Première comparaison : cible + besoin + objectif. Aucun score pondéré n'est
    # utilisé ; CAP retient le groupe qui réunit le plus de critères essentiels.
    max_core = max(item["core_count"] for item in evidence.values())
    core_candidates = [p for p, item in evidence.items() if item["core_count"] == max_core]
    max_depth = max(evidence[p]["strategic_depth"] for p in core_candidates)
    close_candidates = [p for p in core_candidates if evidence[p]["strategic_depth"] == max_depth]

    if len(close_candidates) == 1:
        winner = close_candidates[0]
        winner_base = evidence[winner]["core_count"] - int(evidence[winner].get("external_match", False))
        externally_separated = any(
            platform != winner
            and evidence[platform]["core_count"] - int(evidence[platform].get("external_match", False)) == winner_base
            and evidence[platform]["strategic_depth"] == evidence[winner]["strategic_depth"]
            and evidence[winner].get("external_match", False)
            and not evidence[platform].get("external_match", False)
            for platform in evidence
        )
        reason = "recherche externe" if externally_separated else "croisement cible–besoin–objectif"
        return winner, reason, close_candidates

    # Lorsque plusieurs plateformes sont stratégiquement proches, les moyens
    # peuvent les départager. Un manque sur la plateforme gagnante n'est donc pas
    # ignoré, mais il ne remplace pas une nette supériorité stratégique.
    best_feasibility = min(feasibility[p]["rank"] for p in close_candidates)
    operational = [p for p in close_candidates if feasibility[p]["rank"] == best_feasibility]
    if len(operational) == 1:
        return operational[0], "moyens du cabinet", close_candidates

    best_external = max(evidence[p]["external_rank"] for p in operational)
    researched = [p for p in operational if evidence[p]["external_rank"] == best_external]
    if len(researched) == 1:
        return researched[0], "recherche externe", close_candidates

    best_target = max(evidence[p]["target_fit"] for p in researched)
    targeted = [p for p in researched if evidence[p]["target_fit"] == best_target]
    if len(targeted) == 1:
        return targeted[0], "données de cible", close_candidates

    winner = min(targeted, key=PLATFORM_NAMES.index)
    return winner, "règle stable de départage", close_candidates


def _complementary_platform(
    answers: dict,
    winner: str,
    close_candidates: list[str],
    evidence: dict[str, dict],
    feasibility: dict[str, dict],
) -> tuple[str | None, str | None]:
    if TIME_ORDER.get(answers.get("q8"), 0) < TIME_ORDER["6 à 10 h"]:
        return None, None

    alternatives = [platform for platform in close_candidates if platform != winner]
    eligible: list[str] = []
    for platform in alternatives:
        if feasibility[platform]["label"] == "Lancement à reporter":
            continue
        if (winner, platform) not in CONTENT_REUSE_PAIRS:
            continue
        if not feasibility[platform]["compatible_formats"]:
            continue
        if not (evidence[platform]["observed"] or evidence[platform]["external_rank"] >= 2):
            continue
        eligible.append(platform)

    if not eligible:
        return None, None
    complement = min(
        eligible,
        key=lambda platform: (
            feasibility[platform]["rank"],
            -evidence[platform]["external_rank"],
            PLATFORM_NAMES.index(platform),
        ),
    )
    reason = (
        f"{complement} peut relayer les contenus de {winner} sans créer une seconde ligne éditoriale complète."
    )
    return complement, reason


def _selection_reasons(
    answers: dict,
    winner: str,
    need_analysis: dict,
    evidence: dict[str, dict],
    tie_break: str,
    external_research: dict | None,
) -> list[str]:
    item = evidence[winner]
    reasons = [need_analysis["explanation"]]
    objective = answers.get("custom_objective") if answers.get("q6") == "Autre" else answers.get("q6")
    if item["objective_fit"]:
        reasons.append(
            f"Le rôle de {winner} est cohérent avec l’objectif « {objective} »."
        )
    if item["observed"]:
        reasons.append(f"{winner} fait partie des réseaux observés auprès du persona.")
    elif item["reference"]:
        reasons.append(f"Le référentiel du persona apporte un indice favorable à {winner}.")
    if item["external_signal"] in {"fort", "modéré"}:
        reasons.append(
            f"La recherche publique a relevé un signal {item['external_signal']} pour le sujet étudié sur {winner}."
        )
    elif external_research and external_research.get("status") == "fallback":
        reasons.append(
            "La recherche publique n’était pas disponible ; la décision repose alors sur les données du cabinet et le référentiel CAP."
        )
    if tie_break == "moyens du cabinet":
        reasons.append(
            f"Parmi les plateformes stratégiquement proches, {winner} est la plus compatible avec les moyens déclarés."
        )
    return list(dict.fromkeys(reasons))


def _non_priority_reasons(
    winner: str,
    complementary: str | None,
    evidence: dict[str, dict],
    feasibility: dict[str, dict],
) -> dict[str, str]:
    reasons: dict[str, str] = {}
    winner_item = evidence[winner]
    for platform in PLATFORM_NAMES:
        if platform == winner:
            continue
        if platform == complementary:
            reasons[platform] = "Retenue comme plateforme complémentaire, et non comme second canal prioritaire."
            continue
        item = evidence[platform]
        if item["core_count"] < winner_item["core_count"]:
            reasons[platform] = "Répond moins complètement au croisement entre la cible, le besoin et l’objectif."
        elif item["strategic_depth"] < winner_item["strategic_depth"]:
            reasons[platform] = "Correspond au public, mais moins directement au besoin et à l’objectif prioritaires."
        elif feasibility[platform]["rank"] > feasibility[winner]["rank"]:
            reasons[platform] = "Nécessite davantage d’ajustements au regard des formats, du temps ou des ressources déclarés."
        elif item["external_rank"] < winner_item["external_rank"]:
            reasons[platform] = "Les signaux publics trouvés sont moins favorables pour le sujet étudié."
        else:
            reasons[platform] = "Reste utilisable, mais n’apporte pas un avantage suffisant pour devenir prioritaire."
    return reasons


def compare_platforms(answers: dict, external_research: dict | None = None) -> dict:
    control = strategic_control(answers)
    if control["status"] != "Choix validé":
        return {
            "winner": None,
            "complementary_platform": None,
            "comparison": {},
            "tie_break": None,
            "outcome": "invalid_data",
            "need_analysis": classify_need(answers.get("priority_need", "")),
            "close_candidates": [],
            "feasibility_by_platform": {},
        }

    need_analysis = classify_need(answers.get("priority_need", ""))
    evidence = {
        platform: _platform_evidence(answers, platform, need_analysis, external_research)
        for platform in PLATFORM_NAMES
    }
    feasibility = {
        platform: evaluate_feasibility(answers, platform)
        for platform in PLATFORM_NAMES
    }
    winner, tie_break, close_candidates = _choose_winner(answers, evidence, feasibility)
    complement, complement_reason = _complementary_platform(
        answers, winner, close_candidates, evidence, feasibility
    )

    return {
        "winner": winner,
        "complementary_platform": complement,
        "complementary_reason": complement_reason,
        "comparison": evidence,
        "tie_break": tie_break,
        "outcome": "recommended",
        "need_analysis": need_analysis,
        "close_candidates": close_candidates,
        "feasibility_by_platform": feasibility,
    }


def evaluate(answers: dict, external_research: dict | None = None) -> dict:
    control = strategic_control(answers)
    if control["status"] != "Choix validé":
        empty_feasibility = evaluate_feasibility(answers, None)
        return {
            "strategic_status": control["status"],
            "blocking_reason": " ".join(control["blocking"]) or None,
            "decision_notes": control["blocking"],
            "winner": None,
            "complementary_platform": None,
            "recommended_platforms": [],
            "retained_platform": None,
            "selection_outcome": "invalid_data",
            "comparison": {},
            "tie_break": None,
            "selection_reasons": [],
            "non_priority_reasons": {},
            "need_analysis": classify_need(answers.get("priority_need", "")),
            "feasibility_label": empty_feasibility["label"],
            "feasibility_rows": empty_feasibility["rows"],
            "launch_actions": empty_feasibility["actions"],
            "actors": empty_feasibility["actors"],
            "external_research": external_research or {},
            "alerts": control["blocking"],
        }

    selection = compare_platforms(answers, external_research)
    winner = selection["winner"]
    complementary = selection["complementary_platform"]
    feasibility_by_platform = selection["feasibility_by_platform"]
    feasibility = feasibility_by_platform[winner]
    evidence = selection["comparison"]

    return {
        "strategic_status": "Choix validé",
        "blocking_reason": None,
        "decision_notes": [],
        "winner": winner,
        "complementary_platform": complementary,
        "complementary_reason": selection.get("complementary_reason"),
        "recommended_platforms": [winner],
        "retained_platform": None,
        "selection_outcome": "recommended",
        "comparison": evidence,
        "tie_break": selection["tie_break"],
        "selection_reasons": _selection_reasons(
            answers,
            winner,
            selection["need_analysis"],
            evidence,
            selection["tie_break"],
            external_research,
        ),
        "non_priority_reasons": _non_priority_reasons(
            winner, complementary, evidence, feasibility_by_platform
        ),
        "need_analysis": selection["need_analysis"],
        "feasibility_label": feasibility["label"],
        "feasibility_rows": feasibility["rows"],
        "launch_actions": feasibility["actions"],
        "feasibility_by_platform": feasibility_by_platform,
        "actors": feasibility["actors"],
        "external_research": external_research or {},
        "alerts": feasibility["actions"],
    }
