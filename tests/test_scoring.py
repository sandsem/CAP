import unittest

from scoring import (
    compare_platforms,
    evaluate,
    required_skills_for_formats,
    strategic_control,
)


def base_answers():
    return {
        "q1": "Oui",
        "q2": ["Start-up", "Profession libérale / Freelance"],
        "q2_coherence": "Oui",
        "q3": "Oui",
        "priority_need": "Structurer et développer son activité",
        "q4": ["Instagram", "TikTok"],
        "q4_modes": ["Découverte visuelle en suivant des comptes"],
        "q5": ["Expérience terrain", "Étude sectorielle"],
        "q5_quality": "Récentes et concordantes",
        "q6": "Acquisition",
        "q6_treatment": "Montrer et vulgariser visuellement",
        "q6_effect": "Valoriser l’image du cabinet et entretenir la relation",
        "indicator": "Prises de contact qualifiées",
        "target": "2",
        "deadline": "3 mois",
        "q7": {
            "Facebook": "Aucun compte",
            "Instagram": "Compte actif",
            "TikTok": "Aucun compte",
            "YouTube": "Aucun compte",
        },
        "q8": "6 à 10 h",
        "q14": ["Carrousel", "Reel"],
        "q9": {
            "Rédaction / script": "Autonome",
            "Création de visuels": "Autonome",
            "Montage vidéo": "Autonome",
        },
        "q10": [
            "Smartphone récent",
            "Ordinateur",
            "Connexion stable",
            "Micro",
        ],
        "q11": "Expert-comptable",
        "q12": ["Aucun appui"],
        "q12_status": "Aucune aide nécessaire",
        "q13": "Budget validé",
        "q15": None,
    }


class StrategicTests(unittest.TestCase):
    def test_instagram_recommended_from_observed_usage(self):
        result = evaluate(base_answers())
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(result["strategic_status"], "Choix validé")
        self.assertNotIn("scores", result)
        self.assertNotIn("guide", result)

    def test_generic_profile_does_not_score_platforms(self):
        answers = base_answers()
        answers["q2"] = ["Artisan / commerçant / restaurateur"]
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")

    def test_target_network_is_an_eligibility_filter(self):
        answers = base_answers()
        answers["q4"] = ["TikTok"]
        answers["q4_modes"] = [
            "Recommandation de contenus selon les centres d’intérêt"
        ]
        answers["q6_treatment"] = (
            "Capter rapidement avec un contenu direct et incarné"
        )
        answers["q6_effect"] = "Faire découvrir le cabinet"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "TikTok")

    def test_youtube_matches_search_and_expertise(self):
        answers = base_answers()
        answers["q4"] = ["YouTube"]
        answers["q4_modes"] = ["Recherche volontaire d’une réponse"]
        answers["q6"] = "Expertise / conseil"
        answers["q6_treatment"] = "Expliquer et approfondir un sujet"
        answers["q6_effect"] = (
            "Démontrer l’expertise et répondre à un besoin identifié"
        )
        answers["q14"] = ["Vidéo longue"]
        result = evaluate(answers)
        self.assertEqual(result["winner"], "YouTube")

    def test_facebook_matches_community_and_proximity(self):
        answers = base_answers()
        answers["q4"] = ["Facebook"]
        answers["q4_modes"] = [
            "Échanges dans une communauté ou un groupe local"
        ]
        answers["q6"] = "Fidélisation"
        answers["q6_treatment"] = "Informer et échanger avec une communauté"
        answers["q6_effect"] = "Créer une relation de proximité"
        answers["q14"] = ["Publication texte"]
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Facebook")

    def _tie_answers(self):
        answers = base_answers()
        answers["q4_modes"] = ["Plusieurs usages"]
        answers["q6_treatment"] = "Informer et échanger avec une communauté"
        answers["q6_effect"] = "Créer une relation de proximité"
        answers["q7"]["Instagram"] = "Compte inactif"
        answers["q7"]["TikTok"] = "Compte inactif"
        return answers

    def test_results_already_obtained_break_tie_first(self):
        answers = self._tie_answers()
        answers["q7"]["Instagram"] = "Contacts obtenus"
        answers["q7"]["TikTok"] = "Compte actif"
        selection = compare_platforms(answers)
        self.assertEqual(selection["winner"], "Instagram")
        self.assertEqual(
            selection["tie_break"],
            "résultats déjà obtenus auprès de la cible",
        )

    def test_active_account_breaks_tie_without_results(self):
        answers = self._tie_answers()
        answers["q7"]["Instagram"] = "Compte actif"
        selection = compare_platforms(answers)
        self.assertEqual(selection["winner"], "Instagram")
        self.assertEqual(selection["tie_break"], "compte déjà actif")

    def test_equality_is_not_forced(self):
        answers = self._tie_answers()
        selection = compare_platforms(answers)
        self.assertIsNone(selection["winner"])
        self.assertEqual(set(selection["tied_platforms"]), {"Instagram", "TikTok"})

    def test_observation_choice_does_not_become_false_recommendation(self):
        answers = self._tie_answers()
        answers["q15"] = "TikTok"
        answers["q14"] = ["Vidéo"]
        result = evaluate(answers)
        self.assertIsNone(result["winner"])
        self.assertEqual(result["observation_platform"], "TikTok")
        self.assertEqual(result["platform_for_launch"], "TikTok")

    def test_missing_source_blocks_recommendation(self):
        answers = base_answers()
        answers["q5"] = ["Aucune source"]
        result = evaluate(answers)
        self.assertEqual(result["strategic_status"], "Recommandation impossible")
        self.assertIsNone(result["winner"])

    def test_partial_information_requires_review_but_keeps_orientation(self):
        answers = base_answers()
        answers["q5"] = ["Expérience terrain"]
        result = evaluate(answers)
        self.assertEqual(result["strategic_status"], "Projet à revoir")
        self.assertEqual(result["winner"], "Instagram")

    def test_old_information_blocks_recommendation(self):
        answers = base_answers()
        answers["q5_quality"] = "Anciennes ou non vérifiées"
        control = strategic_control(answers)
        self.assertEqual(control["status"], "Recommandation impossible")


class FeasibilityTests(unittest.TestCase):
    def test_formats_trigger_only_needed_skills(self):
        self.assertEqual(
            required_skills_for_formats(["Carrousel"]),
            {"Rédaction / script", "Création de visuels"},
        )
        self.assertEqual(
            required_skills_for_formats(["Reel"]),
            {"Rédaction / script", "Montage vidéo"},
        )

    def test_all_green_means_project_ready(self):
        result = evaluate(base_answers())
        self.assertEqual(result["feasibility_label"], "Projet prêt")
        self.assertTrue(
            all(row["status"] == "vert" for row in result["feasibility_rows"])
        )

    def test_orange_requires_preparation(self):
        answers = base_answers()
        answers["q8"] = "Moins de 2 h"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(result["feasibility_label"], "Lancement à préparer")

    def test_one_red_postpones_launch_without_changing_platform(self):
        answers = base_answers()
        answers["q9"]["Montage vidéo"] = "À acquérir"
        answers["q12_status"] = "Aide indispensable sans solution"
        result = evaluate(answers)
        self.assertEqual(result["winner"], "Instagram")
        self.assertEqual(result["feasibility_label"], "Lancement à reporter")
        self.assertTrue(
            any(row["status"] == "rouge" for row in result["feasibility_rows"])
        )


if __name__ == "__main__":
    unittest.main()
