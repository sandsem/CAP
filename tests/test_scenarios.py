import unittest

from config import INDICATORS_BY_OBJECTIVE, PERSONA_PLATFORM_REFERENCE, PLATFORM_NAMES
from scoring import evaluate
from tests.test_scoring import base_answers


PROFILES = list(PERSONA_PLATFORM_REFERENCE)
OBJECTIVES = [
    "Visibilité et notoriété",
    "Acquisition",
    "Expertise et conseil",
    "Recrutement",
    "Fidélisation",
]
NETWORK_CASES = ["inconnu"] + PLATFORM_NAMES


def _scenario_test(profile: str, objective: str, network_case: str):
    def test(self):
        answers = base_answers()
        answers["q2"] = [profile]
        answers["custom_profile"] = "Persona métier spécifique" if profile == "Autre" else ""
        answers["q6"] = objective
        answers["indicator"] = next(
            item for item in INDICATORS_BY_OBJECTIVE[objective]
            if item != "Autre indicateur"
        )
        if objective == "Recrutement":
            answers["priority_need"] = "Recruter un jeune collaborateur ou un alternant"
        elif objective == "Fidélisation":
            answers["priority_need"] = "Maintenir une relation régulière avec les clients existants"
        elif objective == "Visibilité et notoriété":
            answers["priority_need"] = "Faire connaître le cabinet et ses domaines d’intervention"
        elif objective == "Expertise et conseil":
            answers["priority_need"] = "Expliquer un choix fiscal et juridique complexe"
        else:
            answers["priority_need"] = "Présenter les solutions proposées par le cabinet"

        if network_case == "inconnu":
            answers.update({
                "q4": ["Je ne sais pas"],
                "q4_priority": "Je ne sais pas",
                "q5": [],
                "q5_quality": None,
            })
        else:
            answers.update({
                "q4": [network_case],
                "q4_priority": network_case,
                "q5": ["Entretiens"],
                "q5_quality": "Oui",
            })

        result = evaluate(answers)
        self.assertEqual(result["strategic_status"], "Choix validé")
        self.assertIn(result["winner"], PLATFORM_NAMES)
        self.assertEqual(result["recommended_platforms"], [result["winner"]])
        self.assertNotEqual(result["selection_outcome"], "tie")
    return test


class DecisionScenarioTests(unittest.TestCase):
    """275 scénarios métier : 11 personas × 5 objectifs × 5 situations réseau."""


index = 0
for profile in PROFILES:
    for objective in OBJECTIVES:
        for network_case in NETWORK_CASES:
            index += 1
            setattr(
                DecisionScenarioTests,
                f"test_scenario_{index:03d}",
                _scenario_test(profile, objective, network_case),
            )


if __name__ == "__main__":
    unittest.main()
