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


def calculate_platform_scores(answers: dict) -> tuple[dict[str, float], str | None, bool]:
    profile_scores = _mean_affinity(answers.get("q2", []), PROFILE_AFFINITY)
    target_networks = [
        network
        for network in answers.get("q4", [])
        if network in PLATFORM_NAMES
    ]
    has_known_network = bool(target_networks)
    objective = answers.get("q6", "Autre")
    objective_scores = OBJECTIVE_AFFINITY.get(
        objective, OBJECTIVE_AFFINITY["Autre"]
    )
    time = answers.get("q8", "Non évalué")
    time_scores = TIME_AFFINITY.get(time, TIME_AFFINITY["Non évalué"])

    weight_total = sum(COHERENCE_WEIGHTS.values())

    scores = {}
    for platform in PLATFORM_NAMES:
        components = {
            "profile": profile_scores[platform],
            "objective": objective_scores[platform],
            "time": time_scores[platform],
        }
        scores[platform] = round(
            sum(
                components[key] * weight
                for key, weight in COHERENCE_WEIGHTS.items()
            )
            / weight_total,
            1,
        )

    # Lorsque les canaux d'information de la cible sont connus, CAP ne
    # recommande pas une plateforme sur laquelle elle ne recherche pas les
    # informations liées au besoin traité par le cabinet. Ce critère forme un
    # filtre. L'objectif SMART départage en priorité les réseaux éligibles,
    # complété par le profil de la cible et, marginalement, par le temps.
    # Si ces canaux sont inconnus, les quatre plateformes restent comparées à
    # titre indicatif.
    eligible_platforms = target_networks if has_known_network else PLATFORM_NAMES
    ranking = sorted(
        ((platform, scores[platform]) for platform in eligible_platforms),
        key=lambda item: item[1],
        reverse=True,
    )
    top_name, top_score = ranking[0]
    unresolved = False

    if len(ranking) == 1:
        return scores, top_name, unresolved

    second_name, second_score = ranking[1]

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
            ranking = sorted(
                ((platform, scores[platform]) for platform in eligible_platforms),
                key=lambda item: item[1],
                reverse=True,
            )
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


def build_reliability_notes(answers: dict) -> list[str]:
    notes = []
    if answers.get("q1") == "Partiellement":
        notes.append("persona à finaliser")

    if answers.get("q3") == "Partiellement":
        notes.append("besoins à compléter")
    elif answers.get("q3") == "Non":
        notes.append("besoins à recenser")

    if not any(network in PLATFORM_NAMES for network in answers.get("q4", [])):
        notes.append("canaux d’information de la cible à documenter")

    sources = [
        source for source in answers.get("q5", []) if source != "Aucune source"
    ]
    if len(sources) == 1:
        notes.append("seconde source à ajouter")
    elif not sources:
        notes.append("sources à documenter")

    return notes


def calculate_readiness(
    answers: dict,
    winner: str | None = None,
) -> tuple[float, str]:
    time_score = {
        "Moins de 2 h": 8,
        "2 à 5 h": 18,
        "6 à 10 h": 26,
        "Plus de 10 h": 30,
        "Non évalué": 0,
    }.get(answers.get("q8"), 0)

    competency_value = {"À acquérir": 0, "Notions": 0.5, "Autonome": 1}
    competencies = answers.get("q9", {})
    required_skills = REQUIRED_SKILLS_BY_PLATFORM.get(winner, set(competencies))
    relevant_competencies = {
        skill: level
        for skill, level in competencies.items()
        if skill in required_skills
    }
    skill_score = 30 * mean(
        competency_value.get(level, 0)
        for level in relevant_competencies.values()
    ) if relevant_competencies else 0

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
    missing_skills = any(
        level == "À acquérir"
        for level in relevant_competencies.values()
    )
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

    # Le niveau de préparation doit rester cohérent avec la plateforme
    # recommandée. Un temps inférieur au minimum de référence empêche
    # d'afficher un lancement immédiatement opérationnel.
    if winner:
        minimum_time = MINIMUM_TIME_BY_PLATFORM[winner]
        time_gap = TIME_RANK[minimum_time] - TIME_RANK.get(
            answers.get("q8", "Non évalué"),
            0,
        )
        if time_gap >= 2:
            score = min(score, 49.0)
        elif time_gap == 1:
            score = min(score, 74.0)

    if score >= 75:
        label = "Prêt à démarrer"
    elif score >= 50:
        label = "À compléter"
    else:
        label = "À préparer"
    return score, label


MINIMUM_TIME_BY_PLATFORM = {
    "Facebook": "2 à 5 h",
    "Instagram": "6 à 10 h",
    "TikTok": "6 à 10 h",
    "YouTube": "Plus de 10 h",
}

TIME_RANK = {
    "Non évalué": 0,
    "Moins de 2 h": 1,
    "2 à 5 h": 2,
    "6 à 10 h": 3,
    "Plus de 10 h": 4,
}

REQUIRED_SKILLS_BY_PLATFORM = {
    "Facebook": {"Rédaction / script", "Création"},
    "Instagram": {"Rédaction / script", "Création", "Montage"},
    "TikTok": {
        "Rédaction / script",
        "Création",
        "Montage",
        "Aisance face caméra",
    },
    "YouTube": {
        "Rédaction / script",
        "Création",
        "Montage",
        "Aisance face caméra",
    },
}


def build_launch_actions(answers: dict, winner: str | None) -> list[str]:
    """Transforme les limites opérationnelles en actions à réaliser avant lancement."""
    actions = []
    time = answers.get("q8", "Non évalué")

    if winner:
        minimum_time = MINIMUM_TIME_BY_PLATFORM[winner]
        if TIME_RANK.get(time, 0) < TIME_RANK[minimum_time]:
            actions.append(
                f"Inscrire au plan de charge une enveloppe de {minimum_time} par mois "
                f"pour préparer, publier et suivre les contenus sur {winner}."
            )
    elif time == "Non évalué":
        actions.append(
            "Évaluer le temps mensuel réellement disponible dans le plan de charge."
        )

    skills = answers.get("q9", {})
    required_skills = REQUIRED_SKILLS_BY_PLATFORM.get(winner, set(skills))
    missing_skills = {
        skill
        for skill in required_skills
        if skills.get(skill, "À acquérir") == "À acquérir"
    }

    if "Rédaction / script" in missing_skills:
        actions.append(
            "Préparer un modèle de script réutilisable avec une accroche, un message "
            "principal et un appel à l’action."
        )

    production_skills = missing_skills.intersection({"Création", "Montage"})
    if production_skills:
        actions.append(
            "Réaliser un premier contenu non publié afin de maîtriser sa création, "
            "son montage et son sous-titrage."
        )

    if "Aisance face caméra" in missing_skills:
        actions.append(
            "Enregistrer deux essais non publiés pour travailler la prise de parole "
            "face caméra avant le premier tournage."
        )

    equipment = set(answers.get("q10", []))
    if not equipment.intersection({"Smartphone récent", "Caméra"}):
        actions.append(
            "Prévoir un smartphone récent ou une caméra avant la première production."
        )
    elif "Connexion stable" not in equipment:
        actions.append(
            "Vérifier une connexion stable pour programmer les publications et "
            "consulter les statistiques."
        )

    if answers.get("q11") == "Non défini":
        actions.append(
            "Désigner la personne responsable de la préparation, de la publication "
            "et du suivi des contenus."
        )

    support = set(answers.get("q12", []))
    if missing_skills and support.intersection({"Aucun appui", "Non défini"}):
        actions.append(
            "Choisir une autoformation, une formation ou un appui externe pour les "
            "compétences qui ne sont pas encore maîtrisées."
        )

    if answers.get("q13") == "Non évalué":
        actions.append(
            "Chiffrer le matériel et les éventuels besoins de formation avant de "
            "valider le budget de lancement."
        )

    if not actions:
        actions.append(
            "Programmer la première publication et fixer un point de contrôle après "
            "un mois pour vérifier la charge réellement consommée."
        )

    return actions


def build_decision_notes(answers: dict, unresolved: bool) -> list[str]:
    """Liste uniquement les données de décision qui doivent encore être fiabilisées."""
    notes = []
    if answers.get("q1") == "Partiellement":
        notes.append("Finaliser le persona de la clientèle recherchée.")
    if answers.get("q3") == "Non":
        notes.append("Recenser les besoins prioritaires de la cible.")
    elif answers.get("q3") == "Partiellement":
        notes.append("Compléter le recensement des besoins de la cible.")
    if not any(network in PLATFORM_NAMES for network in answers.get("q4", [])):
        notes.append(
            "Documenter les réseaux sur lesquels la cible recherche les "
            "informations liées à son besoin."
        )
    sources = [
        source for source in answers.get("q5", []) if source != "Aucune source"
    ]
    if len(sources) < 2:
        notes.append("Croiser les informations du persona avec une seconde source.")
    if unresolved:
        notes.insert(
            0,
            "Préciser le profil cible ou ses canaux d’information pour "
            "départager les plateformes.",
        )
    return notes


def evaluate(answers: dict) -> dict:
    scores, winner, unresolved = calculate_platform_scores(answers)
    reliability, reliability_label = calculate_reliability(answers)
    reliability_notes = build_reliability_notes(answers)
    readiness, readiness_label = calculate_readiness(answers, winner)
    decision_notes = build_decision_notes(answers, unresolved)
    launch_actions = build_launch_actions(answers, winner)
    return {
        "scores": scores,
        "winner": winner,
        "unresolved": unresolved,
        "reliability": reliability,
        "reliability_label": reliability_label,
        "reliability_notes": reliability_notes,
        "readiness": readiness,
        "readiness_label": readiness_label,
        "decision_notes": decision_notes,
        "launch_actions": launch_actions,
        # Conservé pour la compatibilité avec les premières synthèses.
        "alerts": decision_notes + launch_actions,
    }
