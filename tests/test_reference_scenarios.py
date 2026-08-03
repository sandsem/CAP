import unittest

from scoring import evaluate
from tests.test_scoring import base_answers, fake_research


class ReferenceBusinessScenarios(unittest.TestCase):
    """Scénarios de référence avec résultat métier attendu et explicite."""

    def assert_result(self, answers, *, winner, tie_break, feasibility, complement=None, research=None):
        result = evaluate(answers, research)
        self.assertEqual(result["winner"], winner)
        self.assertEqual(result["tie_break"], tie_break)
        self.assertEqual(result["feasibility_label"], feasibility)
        self.assertEqual(result["complementary_platform"], complement)
        self.assertTrue(result["selection_reasons"])
        return result

    def test_complex_transition_keeps_youtube_and_prepares_launch(self):
        answers = base_answers()
        answers.update({
            "q2": ["Micro-entrepreneur"],
            "priority_need": "Passer du statut de micro-entrepreneur à une société",
            "q4": ["Instagram"],
            "q4_priority": "Instagram",
            "q5": ["Entretiens"],
            "q6": "Expertise et conseil",
            "indicator": "Enregistrements ou partages des contenus",
            "q14": ["Carrousel"],
        })
        result = self.assert_result(
            answers,
            winner="YouTube",
            tie_break="croisement cible–besoin–objectif",
            feasibility="Lancement à préparer",
        )
        self.assertIn("explications détaillées", " ".join(result["selection_reasons"]))

    def test_means_choose_instagram_over_tiktok_when_close(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Instagram", "TikTok"],
            "q4_priority": "Je ne sais pas",
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
            "q14": ["Photo", "Carrousel"],
            "q8": "2 à 5 h",
        })
        self.assert_result(
            answers,
            winner="Instagram",
            tie_break="moyens du cabinet",
            feasibility="Projet prêt",
        )

    def test_declared_priority_supports_tiktok_recruitment(self):
        answers = base_answers()
        answers.update({
            "q2": ["Jeune talent / étudiant"],
            "priority_need": "Recruter un jeune collaborateur ou un alternant",
            "q4": ["TikTok", "Instagram"],
            "q4_priority": "TikTok",
            "q5": ["Entretiens"],
            "q6": "Recrutement",
            "indicator": "Candidatures reçues",
            "q14": ["Vidéo courte", "Photo"],
            "q9": {
                "Rédaction / script": "Autonome",
                "Montage vidéo": "Autonome",
                "Création de visuels": "Autonome",
            },
            "q8": "6 à 10 h",
        })
        self.assert_result(
            answers,
            winner="TikTok",
            tie_break="données de cible",
            feasibility="Projet prêt",
            complement="Instagram",
        )

    def test_facebook_fidelity_is_recommended_and_operational(self):
        answers = base_answers()
        answers.update({
            "q2": ["Artisan / commerçant / restaurateur"],
            "priority_need": "Maintenir une relation régulière avec les clients existants",
            "q4": ["Facebook"],
            "q4_priority": "Facebook",
            "q5": ["Entretiens"],
            "q6": "Fidélisation",
            "indicator": "Interactions récurrentes avec les clients",
            "q14": ["Publication texte", "Photo"],
            "q9": {
                "Rédaction / script": "Autonome",
                "Création de visuels": "Autonome",
            },
            "q8": "2 à 5 h",
        })
        self.assert_result(
            answers,
            winner="Facebook",
            tie_break="données de cible",
            feasibility="Projet prêt",
        )

    def test_no_time_does_not_replace_clear_youtube_recommendation(self):
        answers = base_answers()
        answers.update({
            "q2": ["Micro-entrepreneur"],
            "priority_need": "Passer du statut de micro-entrepreneur à une société",
            "q4": ["Instagram"],
            "q4_priority": "Instagram",
            "q5": ["Entretiens"],
            "q6": "Expertise et conseil",
            "indicator": "Enregistrements ou partages des contenus",
            "q14": ["Vidéo longue", "Vidéo courte"],
            "q9": {
                "Rédaction / script": "Autonome",
                "Montage vidéo": "Autonome",
            },
            "q8": "Aucun temps disponible",
        })
        self.assert_result(
            answers,
            winner="YouTube",
            tie_break="croisement cible–besoin–objectif",
            feasibility="Lancement à reporter",
        )

    def test_complete_external_research_can_break_a_close_choice(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Je ne sais pas"],
            "q4_priority": "Je ne sais pas",
            "q5": [],
            "q5_quality": None,
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
            "q14": ["Carrousel", "Vidéo courte"],
            "q9": {
                "Rédaction / script": "Autonome",
                "Création de visuels": "Autonome",
                "Montage vidéo": "Autonome",
            },
        })
        self.assert_result(
            answers,
            winner="TikTok",
            tie_break="recherche externe",
            feasibility="Projet prêt",
            research=fake_research({"TikTok": "fort", "Instagram": "faible"}),
        )

    def test_partial_external_research_is_neutral(self):
        answers = base_answers()
        answers.update({
            "q2": ["Start-up"],
            "priority_need": "Faire connaître le cabinet auprès de nouveaux entrepreneurs",
            "q4": ["Je ne sais pas"],
            "q4_priority": "Je ne sais pas",
            "q5": [],
            "q5_quality": None,
            "q6": "Visibilité et notoriété",
            "indicator": "Portée des publications",
            "q14": ["Carrousel", "Vidéo courte"],
            "q9": {
                "Rédaction / script": "Autonome",
                "Création de visuels": "Autonome",
                "Montage vidéo": "Autonome",
            },
        })
        baseline = evaluate(answers)
        research = fake_research({"TikTok": "fort"})
        research.update({"status": "partiel", "can_influence": False})
        result = evaluate(answers, research)
        self.assertEqual(result["winner"], baseline["winner"])
        self.assertNotEqual(result["tie_break"], "recherche externe")


if __name__ == "__main__":
    unittest.main()
