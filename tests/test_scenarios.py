import itertools
import unittest

from scoring import evaluate
from tests.test_scoring import base_answers


EVIDENCE_CASES = {
    "Récentes et fiables": ("Choix validé", True),
    "Partiellement vérifiées": ("Projet à revoir", False),
    "Anciennes ou non vérifiées": ("Recommandation impossible", False),
}

TIME_CASES = {
    "6 à 10 h": "vert",
    "Moins de 2 h": "orange",
    "Aucun temps disponible": "rouge",
}

BUDGET_CASES = {
    "Aucune dépense nécessaire": "vert",
    "À vérifier": "orange",
    "Non": "rouge",
}

SKILL_CASES = {
    "autonome": "Autonome",
    "a_acquerir": "À acquérir",
}

SUPPORT_CASES = {
    "formation": ["Formation"],
    "a_trouver": ["Solution à trouver"],
}

EQUIPMENT_CASES = {
    "complet": [
        "Smartphone récent",
        "Ordinateur",
        "Connexion stable",
        "Micro",
    ],
    "connexion_a_verifier": [
        "Smartphone récent",
        "Ordinateur",
        "Micro",
    ],
}

STATUS_RANK = {"vert": 0, "orange": 1, "rouge": 2}
LABEL_BY_RANK = {
    0: "Projet prêt",
    1: "Lancement à préparer",
    2: "Lancement à reporter",
}


def _row_status(result: dict, criterion: str) -> str:
    return next(
        row["status"]
        for row in result["feasibility_rows"]
        if row["criterion"] == criterion
    )


def _scenario_test(
    evidence: str,
    time: str,
    budget: str,
    skill_case: str,
    support_case: str,
    equipment_case: str,
):
    def test(self):
        answers = base_answers()
        answers["q5_quality"] = evidence
        answers["q8"] = time
        answers["q13"] = budget
        answers["q9"]["Montage vidéo"] = SKILL_CASES[skill_case]
        answers["q12"] = SUPPORT_CASES[support_case]
        answers["q10"] = EQUIPMENT_CASES[equipment_case]

        result = evaluate(answers)
        scenario = (
            evidence,
            time,
            budget,
            skill_case,
            support_case,
            equipment_case,
        )

        expected_strategic_status, recommendation_allowed = EVIDENCE_CASES[evidence]
        self.assertEqual(
            result["strategic_status"],
            expected_strategic_status,
            scenario,
        )
        if recommendation_allowed:
            self.assertEqual(result["winner"], "Instagram", scenario)
        else:
            self.assertIsNone(result["winner"], scenario)
            self.assertIsNone(result["platform_for_launch"], scenario)

        expected_time = TIME_CASES[time]
        expected_budget = BUDGET_CASES[budget]
        expected_equipment = (
            "vert" if equipment_case == "complet" else "orange"
        )
        if skill_case == "autonome":
            expected_skill = "vert"
        elif support_case == "formation":
            expected_skill = "orange"
        else:
            expected_skill = "rouge"

        self.assertEqual(
            _row_status(result, "Temps disponible"),
            expected_time,
            scenario,
        )
        self.assertEqual(
            _row_status(result, "Formats et compétences"),
            expected_skill,
            scenario,
        )
        self.assertEqual(
            _row_status(result, "Matériel"),
            expected_equipment,
            scenario,
        )
        self.assertEqual(
            _row_status(result, "Responsable"),
            "vert",
            scenario,
        )
        self.assertEqual(
            _row_status(result, "Budget"),
            expected_budget,
            scenario,
        )
        self.assertEqual(len(result["feasibility_rows"]), 5, scenario)

        worst_rank = max(
            STATUS_RANK[expected_time],
            STATUS_RANK[expected_budget],
            STATUS_RANK[expected_skill],
            STATUS_RANK[expected_equipment],
        )
        self.assertEqual(
            result["feasibility_label"],
            LABEL_BY_RANK[worst_rank],
            scenario,
        )

    return test


class DecisionMatrixTests(unittest.TestCase):
    """216 scénarios distincts générés à partir des paramètres du diagnostic."""


SCENARIOS = itertools.product(
    EVIDENCE_CASES,
    TIME_CASES,
    BUDGET_CASES,
    SKILL_CASES,
    SUPPORT_CASES,
    EQUIPMENT_CASES,
)

for index, values in enumerate(SCENARIOS, start=1):
    setattr(
        DecisionMatrixTests,
        f"test_scenario_{index:03d}",
        _scenario_test(*values),
    )

