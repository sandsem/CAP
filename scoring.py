from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re
import unicodedata

from config import (
    CONTENT_REUSE_PAIRS,
    FORMAT_REQUIRED_SKILLS,
    INDICATOR_OPTIONS,
    INDICATORS_BY_OBJECTIVE,
    MAX_INDICATOR_LENGTH,
    MAX_NEED_LENGTH,
    MAX_OBJECTIVE_LENGTH,
    MAX_PILOT_LENGTH,
    MAX_PROFILE_LENGTH,
    MAX_SOURCE_DETAIL_LENGTH,
    NEED_CATEGORY_KEYWORDS,
    NEED_PLATFORM_PRIORITY,
    NO_PILOT,
    OBJECTIVE_PRIORITY_PLATFORMS,
    OUT_OF_SCOPE_NETWORK,
    PERSONA_PLATFORM_REFERENCE,
    PLATFORM_ESSENTIAL_FORMATS,
    PLATFORM_FORMATS,
    PLATFORM_MINIMUM_HOURS,
    PLATFORM_NAMES,
    PLATFORM_RELAY_EXTRA_HOURS,
    PLATFORM_ROLES,
    TIME_CAPACITY_UPPER_HOURS,
    UNKNOWN_NETWORK,
    VIDEO_FORMATS,
    VISUAL_FORMATS,
)

STATUS_ORDER = {"vert": 0, "orange": 1, "rouge": 2}
EXTERNAL_SIGNAL_ORDER = {"fort": 3, "modéré": 2, "faible": 1, "indisponible": 0}
DEADLINE_UNITS = {
    "jour", "jours", "semaine", "semaines", "mois", "an", "ans", "année", "années"
}


def required_skills_for_formats(formats: list[str], appears_on_camera: bool = False) -> set[str]:
    required: set[str] = set()
    for content_format in formats:
        required.update(FORMAT_REQUIRED_SKILLS.get(content_format, set()))
    if appears_on_camera and set(formats).intersection(VIDEO_FORMATS):
        required.add("Aisance face caméra")
    return required


def _known_networks(answers: dict) -> list[str]:
    return [network for network in answers.get("q4", []) if network in PLATFORM_NAMES]


def _normalise(text: str) -> str:
    value = unicodedata.normalize("NFKD", str(text or ""))
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", value.lower()).strip()


def validate_target_value(value: str | int | float) -> bool:
    text = str(value).strip().replace(" ", "")
    if not re.fullmatch(r"\+?\d+(?:[,.]\d+)?%?", text):
        return False
    try:
        number = Decimal(text.rstrip("%").replace(",", "."))
    except InvalidOperation:
        return False
    return number > 0


def validate_deadline_value(value: str, today: date | None = None) -> bool:
    text = str(value or "").strip().lower()
    duration = re.fullmatch(
        r"\+?(\d+(?:[,.]\d+)?)\s*(jour|jours|semaine|semaines|mois|an|ans|année|années)",
        text,
    )
    if duration:
        try:
            return Decimal(duration.group(1).replace(",", ".")) > 0
        except InvalidOperation:
            return False

    today = today or date.today()
    for pattern in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern).date() > today
        except ValueError:
            continue
    return False


def contains_sensitive_pattern(value: str) -> bool:
    text = str(value or "")
    email = bool(re.search(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b", text))
    phone = bool(re.search(r"(?<!\d)(?:\+?\d[ .-]?){9,14}(?!\d)", text))
    identifiers = bool(re.search(r"\b(?:siren|siret|n[°o]?\s*client|dossier(?:\s+client)?)\s*[:#-]?\s*\d{5,}\b", text, re.I))
    return email or phone or identifiers


def strategic_control(answers: dict) -> dict:
    blocking: list[str] = []

    if answers.get("q1") != "Oui":
        blocking.append("Finaliser le persona avant de relancer le diagnostic.")

    profiles = list(answers.get("q2", []))
    if len(profiles) != 1:
        blocking.append("Choisir un seul persona pour ce diagnostic.")
    elif profiles[0] == "Autre" and not str(answers.get("custom_profile", "")).strip():
        blocking.append("Préciser le persona à analyser.")

    need = str(answers.get("priority_need", "")).strip()
    if not need:
        blocking.append("Préciser le besoin d’information prioritaire du persona.")

    free_text_fields = {
        "persona": (str(answers.get("custom_profile", "")), MAX_PROFILE_LENGTH),
        "besoin": (need, MAX_NEED_LENGTH),
        "source": (str(answers.get("custom_source_details", "")), MAX_SOURCE_DETAIL_LENGTH),
        "objectif": (str(answers.get("custom_objective", "")), MAX_OBJECTIVE_LENGTH),
        "indicateur": (str(answers.get("custom_indicator", "")), MAX_INDICATOR_LENGTH),
        "responsable": (str(answers.get("custom_pilot", "")), MAX_PILOT_LENGTH),
    }
    if any(contains_sensitive_pattern(value) for value, _limit in free_text_fields.values()):
        blocking.append("Retirer les coordonnées, identifiants ou données de dossier des champs libres.")
    if any(len(value) > limit for value, limit in free_text_fields.values()):
        blocking.append("Réduire la longueur des champs libres avant de relancer le diagnostic.")

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
        if "Autre source" in sources and not str(answers.get("custom_source_details", "")).strip():
            blocking.append("Préciser l’autre source utilisée.")
        if answers.get("q5_quality") != "Oui":
            blocking.append("Vérifier que les informations sur les réseaux utilisés sont récentes et fiables.")
        preferred = known[0] if len(known) == 1 else answers.get("q4_priority")
        if len(known) > 1 and preferred not in known + [UNKNOWN_NETWORK]:
            blocking.append("Indiquer le réseau le plus souvent utilisé ou choisir « Je ne sais pas ».")

    objective = answers.get("q6")
    if objective in {None, "", "Non défini"}:
        blocking.append("Définir l’objectif de communication du cabinet.")
    elif objective == "Autre" and not str(answers.get("custom_objective", "")).strip():
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
        if not validate_target_value(target):
            blocking.append("Indiquer une valeur numérique strictement positive pour le résultat attendu.")
        if not validate_deadline_value(deadline):
            blocking.append(
                "Indiquer une durée positive avec son unité, par exemple « 8 mois », ou une date future."
            )

    return {
        "status": "Choix validé" if not blocking else "Recommandation impossible",
        "blocking": blocking,
        "review": [],
    }


def _contains_keyword(text: str, keyword: str) -> bool:
    normalised_keyword = _normalise(keyword)
    if normalised_keyword.endswith("*"):
        stem = normalised_keyword[:-1]
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(stem)}[a-z0-9]*", text))
    if " " in normalised_keyword:
        return normalised_keyword in text
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(normalised_keyword)}(?![a-z0-9])", text))


def _matched_keywords(text: str, keywords: list[str]) -> list[str]:
    selected: list[str] = []
    for keyword in sorted(keywords, key=lambda item: len(_normalise(item).rstrip("*")), reverse=True):
        if not _contains_keyword(text, keyword):
            continue
        core = _normalise(keyword).rstrip("*")
        if any(core in _normalise(existing).rstrip("*") for existing in selected):
            continue
        selected.append(keyword)
    return selected


def classify_need(priority_need: str) -> dict:
    text = _normalise(priority_need)
    matched_by_category: dict[str, list[str]] = {}
    matches: dict[str, int] = {}
    for category, keywords in NEED_CATEGORY_KEYWORDS.items():
        matched_by_category[category] = _matched_keywords(text, keywords)
        matches[category] = len(matched_by_category[category])
    max_score = max(matches.values(), default=0)
    best_categories = [category for category, score in matches.items() if score == max_score and score > 0]
    best_category = best_categories[0] if len(best_categories) == 1 else "général"
    explanations = {
        "explication approfondie": "Le besoin appelle une explication structurée et durable.",
        "démarche pratique": "Le besoin appelle une méthode, des étapes ou une démonstration.",
        "actualité et échéance": "Le besoin exige une information claire, datée et facilement actualisable.",
        "confiance et réassurance": "Le besoin appelle de la pédagogie et des éléments de réassurance.",
        "recrutement": "Le besoin concerne l’attractivité du cabinet et la présentation de son environnement de travail.",
        "fidélisation": "Le besoin concerne la continuité de la relation avec la clientèle existante.",
        "découverte": "Le besoin vise d’abord à faire connaître le cabinet et ses domaines d’intervention.",
        "général": "Le besoin est général ou combine plusieurs finalités ; CAP croise donc l’ensemble des autres critères.",
    }
    return {
        "category": best_category,
        "platforms": NEED_PLATFORM_PRIORITY.get(best_category, PLATFORM_NAMES),
        "explanation": explanations[best_category],
        "matched_categories": best_categories,
        "matched_keywords": matched_by_category,
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
    if not external_research or not external_research.get("can_influence"):
        return "indisponible"
    return external_research.get("platforms", {}).get(platform, {}).get("signal", "indisponible")


def _platform_evidence(answers: dict, platform: str, need_analysis: dict, external_research: dict | None) -> dict:
    known = _known_networks(answers)
    preferred = answers.get("q4_priority")
    profile = (answers.get("q2") or ["Autre"])[0]
    reference = PERSONA_PLATFORM_REFERENCE.get(profile, PLATFORM_NAMES)
    objective = answers.get("q6")

    observed_rank = 2 if preferred == platform else (1 if platform in known else 0)
    persona_rank = len(reference) - reference.index(platform) if platform in reference else 0
    need_fit = _need_fit(platform, need_analysis["category"])
    objective_fit = _objective_fit(platform, objective)
    external_label = _external_signal(external_research, platform)
    external_rank = EXTERNAL_SIGNAL_ORDER.get(external_label, 0)

    return {
        "platform": platform,
        "target_fit": observed_rank,
        "observed_rank": observed_rank,
        "persona_rank": persona_rank,
        "need_fit": need_fit,
        "objective_fit": objective_fit,
        "primary_matches": int(need_fit == 2) + int(objective_fit == 2),
        "compatible_matches": int(need_fit > 0) + int(objective_fit > 0),
        "strategic_depth": need_fit + objective_fit,
        "external_signal": external_label,
        "external_rank": external_rank,
        "external_match": external_rank >= 2,
        "observed": platform in known,
        "preferred_observed": preferred == platform,
        "reference": platform in reference,
        "reference_position": reference.index(platform) + 1 if platform in reference else None,
        "role": PLATFORM_ROLES[platform],
    }


def _criterion(name: str, status: str, observation: str, action: str) -> dict:
    return {"criterion": name, "status": status, "observation": observation, "action": action}


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


def _support_for_skill(answers: dict, skill: str) -> tuple[str | None, bool]:
    item = (answers.get("q12_by_skill", {}) or {}).get(skill) or {}
    solution = item.get("solution")
    return solution, bool(solution and solution != "Aucun appui prévu" and item.get("confirmed") == "Oui")


def evaluate_feasibility(answers: dict, platform: str | None) -> dict:
    rows: list[dict] = []
    selected_formats = list(answers.get("q14", []))
    compatible_formats = (
        [fmt for fmt in selected_formats if fmt in PLATFORM_FORMATS.get(platform, set())]
        if platform else selected_formats
    )
    essential_formats = PLATFORM_ESSENTIAL_FORMATS.get(platform, set()) if platform else set()
    selected_essential = sorted(set(compatible_formats).intersection(essential_formats))
    skills = answers.get("q9", {})
    operational = answers.get("q9_operational", {})
    required_skills = required_skills_for_formats(
        compatible_formats,
        appears_on_camera=answers.get("q16") == "Oui",
    )

    time = answers.get("q8")
    available_upper = TIME_CAPACITY_UPPER_HOURS.get(time, 0.0)
    minimum = PLATFORM_MINIMUM_HOURS.get(platform, 2.0) if platform else 2.0
    if available_upper <= 0:
        rows.append(_criterion(
            "Temps disponible", "rouge",
            "Aucun temps n’est défini pour produire, publier et suivre les contenus.",
            "Dégager un temps régulier dans le plan de charge avant de commencer.",
        ))
    elif available_upper < minimum:
        rows.append(_criterion(
            "Temps disponible", "orange",
            f"Le temps déclaré est inférieur au repère de démarrage retenu pour {platform or 'la communication'}.",
            "Simplifier le rythme et les formats, puis vérifier la charge réelle dans le plan de charge avant le lancement.",
        ))
    else:
        rows.append(_criterion(
            "Temps disponible", "vert",
            "Le temps déclaré est compatible avec un démarrage progressif, sous réserve du suivi du temps réel.",
            "Maintenir ce temps dans le plan de charge et le réévaluer chaque mois.",
        ))

    format_status = "vert"
    observations: list[str] = []
    actions: list[str] = []
    if not selected_formats:
        format_status = "rouge"
        observations.append("Aucun format régulier n’a été choisi.")
        actions.append("Choisir les formats que le cabinet pourra réellement produire.")
    elif platform and not compatible_formats:
        format_status = "orange"
        observations.append(f"Les formats actuellement choisis ne sont pas utilisables sur {platform}.")
        actions.append("Se former à un format structurant de la plateforme et prévoir un second format complémentaire avant la première publication.")
    else:
        if platform and essential_formats and not selected_essential:
            format_status = "orange"
            observations.append(f"Aucun format structurant de {platform} n’est actuellement retenu.")
            actions.append(
                "Choisir un format structurant et, si la compétence manque, planifier la formation ou l’appui correspondant avant le lancement."
            )
        if len(set(compatible_formats)) < 2:
            format_status = "orange" if format_status != "rouge" else format_status
            observations.append("La communication repose actuellement sur un seul format compatible.")
            actions.append("Prévoir un second format complémentaire afin de diversifier les publications.")

        for skill in sorted(required_skills):
            level = skills.get(skill, "À acquérir")
            solution, confirmed = _support_for_skill(answers, skill)
            if level == "À acquérir":
                observations.append(f"Compétence à acquérir : {skill}.")
                if confirmed:
                    format_status = "orange" if format_status != "rouge" else format_status
                    actions.append(f"Mettre en œuvre la solution prévue pour « {skill} » avant la première publication.")
                else:
                    format_status = "rouge"
                    actions.append(f"Planifier une formation ou un appui précis pour « {skill} » avant de commencer.")
            elif level == "Notions":
                can_produce = operational.get(skill) == "Oui"
                if can_produce:
                    observations.append(f"Compétence utilisable mais à renforcer : {skill}.")
                else:
                    format_status = "orange" if format_status != "rouge" else format_status
                    observations.append(f"Le niveau actuel en « {skill} » ne permet pas encore de produire le format attendu.")
                    if confirmed:
                        actions.append(f"Réaliser la solution prévue pour « {skill} » avant le lancement.")
                    else:
                        actions.append(f"Renforcer « {skill} » avant le lancement.")

        if not observations:
            observations.append("Un format structurant et un format complémentaire sont réalisables avec les compétences déclarées.")
            actions.append("Aucune action indispensable avant le lancement.")
        elif format_status == "vert" and any(skills.get(skill) == "Notions" for skill in required_skills):
            actions.append("Poursuivre l’entraînement progressivement sans retarder le lancement.")

    rows.append(_criterion(
        "Formats et compétences", format_status,
        " ".join(observations), " ".join(dict.fromkeys(actions)),
    ))

    equipment = set(answers.get("q10", []))
    capture_formats = {"Photo", "Vidéo courte", "Vidéo longue", "Live"}
    needs_capture = bool(set(compatible_formats).intersection(capture_formats))
    has_capture = bool(equipment.intersection({"Smartphone récent", "Caméra", "Studio équipé"}))
    has_device = bool(equipment.intersection({"Smartphone récent", "Caméra", "Ordinateur", "Studio équipé"}))
    missing_equipment = "Aucun matériel" in equipment or not has_device or (needs_capture and not has_capture)
    if missing_equipment:
        funded = answers.get("q13_has_cost") == "Oui" and answers.get("q13_budget_validated") == "Oui"
        rows.append(_criterion(
            "Matériel", "orange" if funded else "rouge",
            "Le matériel disponible ne permet pas encore de produire les formats nécessaires.",
            "Acquérir ou rendre disponible le matériel minimal avant le lancement."
            if funded else "Identifier le matériel minimal et valider son financement avant de commencer.",
        ))
    elif "Connexion internet stable" not in equipment:
        rows.append(_criterion(
            "Matériel", "orange",
            "Le matériel de production est disponible, mais la connexion utilisée reste à vérifier.",
            "Tester la connexion avant la première publication.",
        ))
    else:
        rows.append(_criterion(
            "Matériel", "vert", "Le matériel nécessaire aux formats retenus est disponible.",
            "Aucune action indispensable avant le lancement.",
        ))

    active_pilots = _active_pilots(answers)
    if not active_pilots:
        rows.append(_criterion(
            "Responsable", "rouge", "Aucun responsable n’est encore désigné.",
            "Désigner la personne qui préparera, validera, publiera et suivra les contenus.",
        ))
    else:
        rows.append(_criterion(
            "Responsable", "vert", f"Le pilotage est confié à : {', '.join(active_pilots)}.",
            "Préciser les tâches et le temps attribués à chaque personne dans le plan de charge.",
        ))

    has_cost = answers.get("q13_has_cost")
    budget_validated = answers.get("q13_budget_validated")
    if has_cost not in {"Oui", "Non"}:
        rows.append(_criterion(
            "Budget", "rouge", "L’existence d’une dépense n’a pas été vérifiée.",
            "Identifier les dépenses éventuelles et valider leur financement.",
        ))
    elif has_cost == "Oui" and budget_validated != "Oui":
        rows.append(_criterion(
            "Budget", "rouge", "Une dépense est prévue, mais son financement n’est pas validé.",
            "Valider le budget ou retenir une solution gratuite avant de commencer.",
        ))
    else:
        rows.append(_criterion(
            "Budget", "vert", "Aucune dépense n’est prévue ou le budget nécessaire est validé.",
            "Reporter les montants dans le plan de charge pour suivre le coût réel.",
        ))

    worst = max((STATUS_ORDER[row["status"]] for row in rows), default=1)
    label = {0: "Projet prêt", 1: "Lancement à préparer", 2: "Lancement à reporter"}[worst]
    launch_actions = list(dict.fromkeys(
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
        "actions": launch_actions,
        "rank": rank,
        "compatible_formats": compatible_formats,
        "essential_formats_selected": selected_essential,
        "actors": active_pilots,
        "minimum_hours": minimum,
    }


def _max_candidates(candidates: list[str], evidence: dict[str, dict], key: str) -> list[str]:
    best = max(evidence[p][key] for p in candidates)
    return [p for p in candidates if evidence[p][key] == best]


def _choose_winner(answers: dict, evidence: dict[str, dict], feasibility: dict[str, dict]) -> tuple[str, str, list[str]]:
    candidates = list(PLATFORM_NAMES)
    for key in ("primary_matches", "compatible_matches", "strategic_depth"):
        candidates = _max_candidates(candidates, evidence, key)
        if len(candidates) == 1:
            return candidates[0], "croisement cible–besoin–objectif", candidates

    close_candidates = list(candidates)

    # Lorsque plusieurs plateformes sont stratégiquement proches, les données
    # récentes et fiables fournies par le cabinet priment sur la recherche web.
    if answers.get("q5_quality") == "Oui":
        observed = [p for p in candidates if evidence[p]["observed_rank"] > 0]
        if observed:
            candidates = observed
            candidates = _max_candidates(candidates, evidence, "observed_rank")
            if len(candidates) == 1:
                return candidates[0], "données de cible", close_candidates

    # Les moyens réels départagent ensuite les plateformes encore proches.
    best_feasibility = min(feasibility[p]["rank"] for p in candidates)
    operational = [p for p in candidates if feasibility[p]["rank"] == best_feasibility]
    if len(operational) == 1:
        return operational[0], "moyens du cabinet", close_candidates
    candidates = operational

    # La recherche externe ne peut intervenir qu'en dernier appui et seulement
    # lorsqu'elle couvre équitablement les quatre plateformes.
    if any(evidence[p]["external_rank"] > 0 for p in candidates):
        candidates = _max_candidates(candidates, evidence, "external_rank")
        if len(candidates) == 1:
            return candidates[0], "recherche externe", close_candidates

    candidates = _max_candidates(candidates, evidence, "persona_rank")
    if len(candidates) == 1:
        return candidates[0], "repères du persona", close_candidates

    objective_order = OBJECTIVE_PRIORITY_PLATFORMS.get(answers.get("q6"), PLATFORM_NAMES)
    objective_choice = min(candidates, key=lambda p: objective_order.index(p))
    return objective_choice, "objectif prioritaire", close_candidates

def _complementary_platform(
    answers: dict,
    winner: str,
    close_candidates: list[str],
    evidence: dict[str, dict],
    feasibility: dict[str, dict],
) -> tuple[str | None, str | None]:
    if feasibility[winner]["label"] != "Projet prêt":
        return None, None
    capacity = TIME_CAPACITY_UPPER_HOURS.get(answers.get("q8"), 0.0)
    alternatives = [platform for platform in close_candidates if platform != winner]
    eligible: list[str] = []
    for platform in alternatives:
        if feasibility[platform]["label"] != "Projet prêt":
            continue
        if (winner, platform) not in CONTENT_REUSE_PAIRS:
            continue
        reusable = set(feasibility[winner]["compatible_formats"]).intersection(
            feasibility[platform]["compatible_formats"]
        )
        if not reusable:
            continue
        required_capacity = PLATFORM_MINIMUM_HOURS[winner] + PLATFORM_RELAY_EXTRA_HOURS[platform]
        if capacity < required_capacity:
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
            -evidence[platform]["observed_rank"],
            -evidence[platform]["external_rank"],
            PLATFORM_RELAY_EXTRA_HOURS[platform],
        ),
    )
    extra = PLATFORM_RELAY_EXTRA_HOURS[complement]
    return complement, (
        f"{complement} peut relayer certains contenus de {winner} sans créer une seconde ligne éditoriale. "
        f"Prévoir environ {extra:g} h supplémentaires par mois dans le plan de charge et vérifier le temps réel."
    )


def _need_plain_sentence(category: str, winner: str) -> str | None:
    messages = {
        "explication approfondie": f"Le besoin demande des explications détaillées et durables ; {winner} est bien adapté à ce type de contenu.",
        "démarche pratique": f"Le besoin appelle une méthode ou une démonstration ; {winner} permet de présenter clairement les étapes.",
        "actualité et échéance": f"Le besoin porte sur une information datée ou à actualiser ; {winner} permet de la diffuser de manière régulière.",
        "confiance et réassurance": f"Le besoin nécessite de rassurer et d’expliquer ; {winner} permet d’apporter des réponses pédagogiques.",
        "recrutement": f"Le besoin concerne le recrutement ; {winner} est adapté pour présenter le cabinet et toucher des candidats potentiels.",
        "fidélisation": f"Le besoin concerne la relation avec les clients existants ; {winner} facilite une communication régulière et suivie.",
        "découverte": f"Le besoin vise à faire connaître le cabinet ; {winner} est adapté pour gagner en visibilité auprès de cette cible.",
    }
    return messages.get(category)


def _selection_reasons(
    answers: dict,
    winner: str,
    need_analysis: dict,
    evidence: dict[str, dict],
    feasibility: dict[str, dict],
    tie_break: str,
    external_research: dict | None,
) -> list[str]:
    item = evidence[winner]
    reasons: list[str] = []

    if item["preferred_observed"]:
        reasons.append(f"Vous avez indiqué que votre cible utilise surtout {winner} pour rechercher cette information.")
    elif item["observed"]:
        reasons.append(f"Vous avez identifié {winner} parmi les réseaux réellement utilisés par votre cible.")

    need_sentence = _need_plain_sentence(need_analysis["category"], winner)
    if need_sentence:
        reasons.append(need_sentence)
    else:
        reasons.append(
            "Le besoin renseigné ne favorise pas une seule plateforme. CAP a donc comparé les réseaux observés, l’objectif et les moyens disponibles."
        )

    objective = answers.get("custom_objective") if answers.get("q6") == "Autre" else answers.get("q6")
    indicator = answers.get("indicator")
    if item["objective_fit"]:
        objective_messages = {
            "Visibilité et notoriété": f"Votre objectif est de gagner en visibilité ; {winner} permet de rendre les contenus plus visibles auprès de la cible.",
            "Acquisition": f"Votre objectif est de générer des prises de contact ; {winner} permet d’expliquer le sujet puis d’orienter la cible vers un rendez-vous ou une demande de contact.",
            "Expertise et conseil": f"Votre objectif est de démontrer l’expertise du cabinet ; {winner} permet de développer des explications utiles et crédibles.",
            "Recrutement": f"Votre objectif est de recevoir des candidatures ; {winner} permet de présenter le cabinet et ses opportunités à la cible recherchée.",
            "Fidélisation": f"Votre objectif est de maintenir la relation avec les clients ; {winner} permet de publier des informations régulières et utiles.",
        }
        reasons.append(objective_messages.get(objective, f"{winner} est cohérent avec votre objectif « {objective} »."))
        if indicator:
            reasons.append(f"Le résultat sera suivi avec l’indicateur « {indicator} ».")

    compatible = feasibility[winner].get("compatible_formats", [])
    if compatible:
        reasons.append(
            f"Les formats que vous pouvez produire sur {winner} sont : {', '.join(compatible)}."
        )

    if tie_break == "moyens du cabinet":
        reasons.append(f"Parmi les plateformes encore proches, {winner} demande le moins d’ajustements avec le temps, les formats et les ressources déclarés.")
    elif tie_break == "données de cible" and not item["preferred_observed"]:
        reasons.append(f"Les informations récentes et fiables fournies sur la cible ont renforcé le choix de {winner}.")
    elif tie_break == "recherche externe":
        reasons.append("La vérification externe a confirmé ce choix, sans remplacer les informations fournies par le cabinet.")

    if (
        external_research
        and external_research.get("status") == "complet"
        and item["external_signal"] in {"fort", "modéré"}
        and tie_break != "recherche externe"
    ):
        reasons.append("La vérification externe est cohérente avec la recommandation, mais elle n’a pas été utilisée seule pour choisir la plateforme.")

    return list(dict.fromkeys(reasons))


def _non_priority_reasons(
    answers: dict,
    winner: str,
    complementary: str | None,
    evidence: dict[str, dict],
    feasibility: dict[str, dict],
    need_category: str,
) -> dict[str, str]:
    reasons: dict[str, str] = {}
    winner_item = evidence[winner]
    known = _known_networks(answers)
    for platform in PLATFORM_NAMES:
        if platform == winner:
            continue
        if platform == complementary:
            reasons[platform] = f"{platform} est conservé comme relais complémentaire ; il ne doit pas créer une deuxième organisation de publication au lancement."
            continue

        item = evidence[platform]
        if known and platform not in known and winner in known:
            reasons[platform] = f"Vous n’avez pas identifié {platform} parmi les réseaux utilisés par votre cible, contrairement à {winner}."
        elif item["need_fit"] < winner_item["need_fit"]:
            reasons[platform] = f"{platform} répond moins directement au besoin prioritaire que {winner}."
        elif item["objective_fit"] < winner_item["objective_fit"]:
            objective_label = answers.get('custom_objective') if answers.get('q6') == 'Autre' else answers.get('q6')
            reasons[platform] = f"{platform} répond moins directement à votre objectif « {objective_label} » que {winner}."
        elif feasibility[platform]["rank"] > feasibility[winner]["rank"]:
            blocking = [
                row["criterion"] for row in feasibility[platform].get("rows", [])
                if row["status"] in {"orange", "rouge"}
            ]
            detail = ", ".join(blocking[:3]).lower() or "les moyens disponibles"
            reasons[platform] = f"{platform} demanderait davantage d’ajustements concernant {detail}."
        elif item["observed_rank"] < winner_item["observed_rank"]:
            reasons[platform] = f"Les informations fournies sur la cible sont moins favorables à {platform} qu’à {winner}."
        elif item["persona_rank"] < winner_item["persona_rank"]:
            reasons[platform] = f"En l’absence d’un avantage plus fort, {platform} correspond moins au profil de cible renseigné que {winner}."
        else:
            reasons[platform] = f"{platform} reste possible, mais {winner} correspond mieux au croisement entre la cible, le besoin, l’objectif et les formats disponibles."
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
    feasibility = {platform: evaluate_feasibility(answers, platform) for platform in PLATFORM_NAMES}
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
            answers, winner, selection["need_analysis"], evidence, feasibility_by_platform, selection["tie_break"], external_research
        ),
        "non_priority_reasons": _non_priority_reasons(
            answers, winner, complementary, evidence, feasibility_by_platform, selection["need_analysis"]["category"]
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
