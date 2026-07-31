import unittest

from config import OBJECTIVE_PRIORITY_PLATFORMS, PERSONA_PLATFORM_REFERENCE, PLATFORM_NAMES
from scoring import compare_platforms
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
        if network_case == "inconnu":
            answers.update({
                "q4": ["Je ne sais pas"],
                "q4_priority": "Je ne sais pas",
                "q5": [],
                "q5_quality": None,
            })
            candidates = PERSONA_PLATFORM_REFERENCE[profile]
            priorities = OBJECTIVE_PRIORITY_PLATFORMS[objective]
            expected = [item for item in candidates if item in priorities] or candidates
        else:
            answers.update({
                "q4": [network_case],
                "q4_priority": network_case,
                "q5": ["Entretiens"],
                "q5_quality": "Oui",
            })
            expected = [network_case]

        selection = compare_platforms(answers)
        actual = [selection["winner"]] if selection["winner"] else selection["tied_platforms"]
        self.assertEqual(actual, expected, (profile, objective, network_case))
        self.assertTrue(set(actual).issubset(set(PLATFORM_NAMES)))
    return test


class DecisionScenarioTests(unittest.TestCase):
    """250 scénarios métier : 10 personas × 5 objectifs × 5 situations réseau."""


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
