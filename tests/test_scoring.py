import unittest

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
            "Facebook": "Aucun",
            "Instagram": "Inactif",
            "TikTok": "Aucun",
            "YouTube": "Aucun",
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
        answers["q7"]["Facebook"] = "Inactif"
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

    def test_neutral_information_returns_no_arbitrary_winner(self):
        answers = base_answers()
        answers["q2"] = ["Autre"]
        answers["q4"] = ["Non identifié"]
        answers["q6"] = "Autre"
        answers["q8"] = "Non évalué"
        answers["q7"] = {
            "Facebook": "Aucun",
            "Instagram": "Aucun",
            "TikTok": "Aucun",
            "YouTube": "Aucun",
        }
        result = evaluate(answers)
        self.assertIsNone(result["winner"])


if __name__ == "__main__":
    unittest.main()
