import unittest

from config import COHERENCE_WEIGHTS
from scoring import evaluate


def base_answers():
    return {
        "q1": "Oui",
        "q2": ["Start-up", "Profession libérale / Freelance", "Micro-entrepreneur"],
        "q3": "Oui",
        "q4": ["Instagram", "YouTube"],
        "q5": ["Expérience terrain", "Étude sectorielle"],
        "q6": "Acquisition",
        "indicator": "Prises de contact",
        "target": "2",
        "deadline": "3 mois",
        "q7": {
            "Facebook": "Aucun compte",
            "Instagram": "Compte inactif",
            "TikTok": "Aucun compte",
            "YouTube": "Aucun compte",
        },
        "q8": "6 à 10 h",
        "q9": {
            "Rédaction / script": "Autonome",
            "Création": "Notions",
            "Montage": "Notions",
            "Aisance face caméra": "Notions",
        },
        "q10": [
            "Smartphone récent",
            "Ordinateur",
            "Connexion stable",
            "Micro",
            "Ring light",
        ],
        "q11": "Expert et associé",
        "q12": ["Autoformation"],
        "q13": "50 à 150 €",
    }


class ScoringTests(unittest.TestCase):
    def test_four_decision_dimensions_have_equal_weight(self):
        self.assertEqual(
            COHERENCE_WEIGHTS,
            {
                "profile": 0.25,
                "target_networks": 0.25,
                "objective": 0.25,
                "time": 0.25,
            },
        )

    def test_visib_recommends_instagram(self):
        result = evaluate(base_answers())
        self.assertEqual(result["winner"], "Instagram")
        self.assertGreater(result["scores"]["Instagram"], result["scores"]["YouTube"])

    def test_artisan_facebook_profile(self):
        answers = base_answers()
        answers["q2"] = ["Artisan / commerçant / restaurateur"]
        answers["q4"] = ["Facebook"]
        answers["q6"] = "Fidélisation"
        answers["q8"] = "2 à 5 h"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Facebook")

    def test_expertise_with_time_recommends_youtube(self):
        answers = base_answers()
        answers["q2"] = ["Dirigeant TPE-PME"]
        answers["q4"] = ["YouTube"]
        answers["q6"] = "Expertise / conseil"
        answers["q8"] = "Plus de 10 h"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "YouTube")

    def test_young_audience_tiktok_profile(self):
        answers = base_answers()
        answers["q2"] = ["Jeune talent / étudiant", "Créateur d’entreprise"]
        answers["q4"] = ["TikTok"]
        answers["q6"] = "Visibilité / notoriété"
        answers["q8"] = "6 à 10 h"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "TikTok")

    def test_missing_sources_reduce_reliability(self):
        answers = base_answers()
        answers["q5"] = ["Aucune source"]
        answers["q3"] = "Partiellement"
        result = evaluate(answers)
        self.assertLess(result["reliability"], 75)

    def test_existing_inactive_account_does_not_decide(self):
        answers = base_answers()
        answers["q7"]["Facebook"] = "Compte inactif"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")

    def test_two_target_networks_are_departed_by_other_criteria(self):
        answers = base_answers()
        answers["q4"] = ["Instagram", "TikTok"]
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")

    def test_unknown_target_network_caps_reliability(self):
        answers = base_answers()
        answers["q4"] = ["Non identifié"]
        result = evaluate(answers)
        self.assertLess(result["reliability"], 75)
        self.assertEqual(result["reliability_label"], "Informations partielles")

    def test_target_network_does_not_override_other_criteria(self):
        answers = base_answers()
        answers["q2"] = ["Dirigeant TPE-PME"]
        answers["q4"] = ["TikTok"]
        answers["q6"] = "Fidélisation"
        answers["q8"] = "Moins de 2 h"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Facebook")

    def test_low_readiness_blocks_immediate_tiktok_launch(self):
        answers = base_answers()
        answers["q1"] = "Partiellement"
        answers["q2"] = [
            "Micro-entrepreneur",
            "Artisan / commerçant / restaurateur",
            "Profession libérale / Freelance",
        ]
        answers["q3"] = "Non"
        answers["q4"] = ["TikTok"]
        answers["q6"] = "Expertise / conseil"
        answers["q8"] = "Moins de 2 h"
        answers["q9"] = {
            "Rédaction / script": "À acquérir",
            "Création": "À acquérir",
            "Montage": "À acquérir",
            "Aisance face caméra": "À acquérir",
        }
        answers["q10"] = ["Smartphone récent"]
        answers["q11"] = "Expert-comptable"
        answers["q12"] = ["Autoformation"]
        answers["q13"] = "Moins de 50 €"

        result = evaluate(answers)

        self.assertEqual(result["winner"], "TikTok")
        self.assertEqual(result["readiness_label"], "Lancement à préparer")
        self.assertLess(result["readiness"], 50)
        self.assertTrue(
            any("6 à 10 h" in action for action in result["launch_actions"])
        )

    def test_readiness_uses_platform_relevant_skills(self):
        answers = base_answers()
        answers["q2"] = ["Artisan / commerçant / restaurateur"]
        answers["q4"] = ["Facebook"]
        answers["q6"] = "Fidélisation"
        answers["q8"] = "2 à 5 h"
        answers["q9"]["Rédaction / script"] = "Autonome"
        answers["q9"]["Création"] = "Autonome"
        answers["q9"]["Montage"] = "À acquérir"
        answers["q9"]["Aisance face caméra"] = "À acquérir"
        result = evaluate(answers)

        self.assertEqual(result["winner"], "Facebook")
        self.assertGreaterEqual(result["readiness"], 75)

    def test_neutral_information_returns_no_arbitrary_winner(self):
        answers = base_answers()
        answers["q2"] = ["Autre"]
        answers["q4"] = ["Non identifié"]
        answers["q6"] = "Autre"
        answers["q8"] = "Non évalué"
        answers["q7"] = {
            "Facebook": "Aucun compte",
            "Instagram": "Aucun compte",
            "TikTok": "Aucun compte",
            "YouTube": "Aucun compte",
        }
        result = evaluate(answers)
        self.assertIsNone(result["winner"])


if __name__ == "__main__":
    unittest.main()
