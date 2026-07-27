from statistics import mean

from config import (
    COHERENCE_WEIGHTS,
    OBJECTIVE_AFFINITY,
    PLATFORM_NAMES,
    PROFILE_AFFINITY,
    STATUS_TIE_BREAK,
    TIME_AFFINITY,
)


def _mean_affinity(
    selections: list[str],
    matrix: dict[str, dict[str, float]],
) -> dict[str, float]:
    usable = [selection for selection in selections if selection in matrix]
    if not usable:
        return {platform: 50.0 for platform in PLATFORM_NAMES}
    return {
        platform: mean(matrix[selection][platform] for selection in usable)
        for platform in PLATFORM_NAMES
    }


def _network_affinity(selections: list[str]) -> tuple[dict[str, float], bool]:
    known = [network for network in selections if network in PLATFORM_NAMES]
    if not known:
        return {platform: 0.0 for platform in PLATFORM_NAMES}, False
    return {
        platform: 100.0 if platform in known else 0.0
        for platform in PLATFORM_NAMES
    }, True


def calculate_platform_scores(answers: dict) -> tuple[dict[str, float], str | None, bool]:
    profile_scores = _mean_affinity(answers.get("q2", []), PROFILE_AFFINITY)
    network_scores, has_known_network = _network_affinity(answers.get("q4", []))
    objective = answers.get("q6", "Autre")
    objective_scores = OBJECTIVE_AFFINITY.get(
        objective, OBJECTIVE_AFFINITY["Autre"]
    )
    time = answers.get("q8", "Non évalué")
    time_scores = TIME_AFFINITY.get(time, TIME_AFFINITY["Non évalué"])

    active_weights = dict(COHERENCE_WEIGHTS)
    if not has_known_network:
        active_weights.pop("target_networks")
    weight_total = sum(active_weights.values())

    scores = {}
    for platform in PLATFORM_NAMES:
        components = {
            "profile": profile_scores[platform],
            "target_networks": network_scores[platform],
            "objective": objective_scores[platform],
            "time": time_scores[platform],
        }
        scores[platform] = round(
            sum(components[key] * weight for key, weight in active_weights.items())
            / weight_total,
            1,
        )

    ranking = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top_name, top_score = ranking[0]
    second_name, second_score = ranking[1]
    unresolved = False

    # Le compte existant n'intervient qu'en dernier recours. Une simple
    # ouverture de compte ou un compte inactif ne modifie pas la recommandation.
    if top_score - second_score <= 1.5:
        statuses = answers.get("q7", {})
        top_bonus = STATUS_TIE_BREAK.get(
            statuses.get(top_name, "Aucun compte"), 0
        )
        second_bonus = STATUS_TIE_BREAK.get(
            statuses.get(second_name, "Aucun compte"), 0
        )
        if top_bonus != second_bonus:
            scores[top_name] = round(scores[top_name] + top_bonus, 1)
            scores[second_name] = round(scores[second_name] + second_bonus, 1)
            ranking = sorted(scores.items(), key=lambda item: item[1], reverse=True)
            top_name, top_score = ranking[0]
            second_name, second_score = ranking[1]

    if top_score - second_score <= 1.5:
        top_name = None
        unresolved = True

    return scores, top_name, unresolved


def calculate_reliability(answers: dict) -> tuple[float, str]:
    persona = {"Oui": 25, "Partiellement": 12.5, "Non": 0}.get(
        answers.get("q1"), 0
    )
    needs = {"Oui": 20, "Partiellement": 10, "Non": 0}.get(
        answers.get("q3"), 0
    )

    target_networks = answers.get("q4", [])
    if any(network in PLATFORM_NAMES for network in target_networks):
        networks = 25
    elif "Autre réseau" in target_networks:
        networks = 10
    else:
        networks = 0

    sources = [
        source for source in answers.get("q5", []) if source != "Aucune source"
    ]
    if len(sources) >= 2:
        source_score = 30
    elif len(sources) == 1:
        source_score = 15
    else:
        source_score = 0

    score = float(persona + needs + networks + source_score)

    # Une information structurante manquante empêche de présenter le
    # diagnostic comme pleinement documenté, même si les autres rubriques
    # sont complètes.
    if not any(network in PLATFORM_NAMES for network in target_networks):
        score = min(score, 65.0)
    if answers.get("q3") == "Non":
        score = min(score, 65.0)
    if answers.get("q1") == "Partiellement":
        score = min(score, 74.0)
    if not sources:
        score = min(score, 49.0)
    if score >= 75:
        label = "Informations documentées"
    elif score >= 50:
        label = "Informations partielles"
    else:
        label = "Résultat indicatif"
    return score, label


def calculate_readiness(answers: dict) -> tuple[float, str]:
    time_score = {
        "Moins de 2 h": 8,
        "2 à 5 h": 18,
        "6 à 10 h": 26,
        "Plus de 10 h": 30,
        "Non évalué": 0,
    }.get(answers.get("q8"), 0)

    competency_value = {"À acquérir": 0, "Notions": 0.5, "Autonome": 1}
    competencies = answers.get("q9", {})
    skill_score = 30 * mean(
        competency_value.get(level, 0) for level in competencies.values()
    ) if competencies else 0

    equipment = set(answers.get("q10", []))
    equipment_score = 0
    if "Smartphone récent" in equipment or "Caméra" in equipment:
        equipment_score += 8
    if "Connexion stable" in equipment:
        equipment_score += 5
    if "Ordinateur" in equipment:
        equipment_score += 3
    if equipment.intersection({"Micro", "Ring light", "Studio équipé"}):
        equipment_score += 4

    pilot_score = 0 if answers.get("q11") == "Non défini" else 10

    support = set(answers.get("q12", []))
    missing_skills = any(level == "À acquérir" for level in competencies.values())
    if support.intersection(
        {"Autoformation", "Formation", "Appui interne", "Prestataire externe", "Autre solution"}
    ):
        support_score = 5
    elif not missing_skills and "Aucun appui" in support:
        support_score = 5
    elif "Aucun appui" in support:
        support_score = 1
    else:
        support_score = 0

    budget_score = {
        "Aucun budget": 3,
        "Moins de 50 €": 4,
        "50 à 150 €": 5,
        "Plus de 150 €": 5,
        "Non évalué": 0,
    }.get(answers.get("q13"), 0)

    score = round(
        min(
            100,
            time_score
            + skill_score
            + equipment_score
            + pilot_score
            + support_score
            + budget_score,
        ),
        1,
    )
    if score >= 75:
        label = "Prêt à démarrer"
    elif score >= 50:
        label = "À consolider"
    else:
        label = "À préparer"
    return score, label


def build_alerts(
    answers: dict,
    reliability: float,
    readiness: float,
    unresolved: bool,
) -> list[str]:
    alerts = []
    if answers.get("q3") == "Non":
        alerts.append("Recenser les besoins prioritaires de la cible.")
    elif answers.get("q3") == "Partiellement":
        alerts.append("Compléter le recensement des besoins de la cible.")

    if not any(network in PLATFORM_NAMES for network in answers.get("q4", [])):
        alerts.append("Documenter les réseaux réellement utilisés par la cible.")

    sources = [
        source for source in answers.get("q5", []) if source != "Aucune source"
    ]
    if len(sources) < 2:
        alerts.append("Croiser les informations du persona avec une seconde source.")

    if answers.get("q8") == "Non évalué":
        alerts.append("Évaluer le temps mensuel disponible dans le plan de charge.")
    elif answers.get("q8") == "Moins de 2 h":
        alerts.append("Prévoir un rythme de publication compatible avec le temps disponible.")

    skills = answers.get("q9", {})
    if any(level == "À acquérir" for level in skills.values()):
        alerts.append("Prévoir l’apprentissage ou l’appui nécessaire aux compétences manquantes.")

    equipment = set(answers.get("q10", []))
    if not equipment.intersection({"Smartphone récent", "Caméra"}):
        alerts.append("Prévoir un équipement permettant de produire les premiers contenus.")
    if "Connexion stable" not in equipment:
        alerts.append("Sécuriser une connexion adaptée à la publication des contenus.")
    if answers.get("q11") == "Non défini":
        alerts.append("Désigner la personne qui pilotera la communication.")
    if answers.get("q13") == "Non évalué":
        alerts.append("Évaluer le budget mobilisable, même s’il reste limité.")
    if unresolved:
        alerts.insert(
            0,
            "Préciser le profil cible ou ses réseaux d’information pour départager les plateformes.",
        )

    if reliability >= 75 and readiness >= 75 and not alerts:
        alerts.append("Aucun point bloquant identifié à ce stade.")
    return alerts


def evaluate(answers: dict) -> dict:
    scores, winner, unresolved = calculate_platform_scores(answers)
    reliability, reliability_label = calculate_reliability(answers)
    readiness, readiness_label = calculate_readiness(answers)
    alerts = build_alerts(answers, reliability, readiness, unresolved)
    return {
        "scores": scores,
        "winner": winner,
        "unresolved": unresolved,
        "reliability": reliability,
        "reliability_label": reliability_label,
        "readiness": readiness,
        "readiness_label": readiness_label,
        "alerts": alerts,
    }
