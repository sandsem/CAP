import unittest

from streamlit.testing.v1 import AppTest


class AppSmokeTests(unittest.TestCase):
    ANSWERS = {
        "q1": "Oui",
        "q2": ["Profession libérale / Freelance"],
        "q2_coherence": "Oui",
        "q3": "Oui",
        "priority_need": "Structurer et développer son activité",
        "q4": ["Instagram", "TikTok"],
        "q4_modes_by_network": {
            "Instagram": "Découverte visuelle en suivant des comptes",
            "TikTok": "Recommandation de contenus selon les centres d’intérêt",
        },
        "q5": ["Expérience terrain", "Étude sectorielle"],
        "q5_quality": "Récentes et fiables",
        "q6": "Acquisition",
        "indicator": "Prises de contact qualifiées",
        "target": "2",
        "deadline": "3 mois",
        "q7": {
            "Facebook": "Aucun résultat identifié",
            "Instagram": "Contacts obtenus",
            "TikTok": "Aucun résultat identifié",
            "YouTube": "Aucun résultat identifié",
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
        ],
        "q11": "Expert-comptable",
        "q12": [],
        "q13": "Aucune dépense nécessaire",
        "q15": None,
        "q16": "Non",
    }

    def test_home_and_prepare_render(self):
        app = AppTest.from_file("app.py", default_timeout=10).run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Commencer", [button.label for button in app.button])
        app.button(key="start").click().run()
        self.assertEqual(len(app.exception), 0)

    def test_review_precedes_result(self):
        app = AppTest.from_file("app.py", default_timeout=10)
        app.session_state["screen"] = "review"
        app.session_state["answers"] = self.ANSWERS
        app.session_state["result"] = None
        app.session_state["return_to_review"] = False
        app.run()

        self.assertEqual(len(app.exception), 0)
        app.button(key="forward_from_review").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["screen"], "result")
        self.assertEqual(app.session_state["result"]["winner"], "Instagram")

    def test_resources_page_does_not_reveal_recommendation(self):
        app = AppTest.from_file("app.py", default_timeout=10)
        app.session_state["screen"] = "resources"
        app.session_state["answers"] = self.ANSWERS
        app.session_state["result"] = None
        app.session_state["return_to_review"] = False
        app.run()

        self.assertEqual(len(app.exception), 0)
        messages = [element.value for element in app.info]
        self.assertFalse(any("Instagram" in message for message in messages))
        self.assertFalse(any("TikTok" in message for message in messages))

    def test_review_status_does_not_display_a_platform_recommendation(self):
        answers = dict(self.ANSWERS)
        answers["q5_quality"] = "Partiellement vérifiées"
        app = AppTest.from_file("app.py", default_timeout=10)
        app.session_state["screen"] = "result"
        app.session_state["answers"] = answers
        from scoring import evaluate

        app.session_state["result"] = evaluate(answers)
        app.session_state["return_to_review"] = False
        app.run()

        self.assertEqual(len(app.exception), 0)
        self.assertIsNone(app.session_state["result"]["winner"])
        rendered = " ".join(
            element.value for element in app.markdown if hasattr(element, "value")
        )
        self.assertIn("Aucune plateforme ne peut être recommandée", rendered)
        self.assertNotIn("Actions nécessaires", rendered)

    def test_target_page_uses_one_persona_and_simple_wording(self):
        app = AppTest.from_file("app.py", default_timeout=10)
        app.session_state["screen"] = "target"
        app.session_state["answers"] = self.ANSWERS
        app.session_state["result"] = None
        app.session_state["return_to_review"] = False
        app.run()

        self.assertEqual(len(app.exception), 0)
        labels = [radio.label for radio in app.radio]
        labels.extend(selectbox.label for selectbox in app.selectbox)
        labels.extend(text.label for text in app.text_input)
        rendered_labels = " ".join(labels)
        self.assertIn("Persona défini ?", rendered_labels)
        self.assertIn("Quel persona souhaitez-vous analyser ?", rendered_labels)
        self.assertNotIn("Persona finalisé ?", rendered_labels)
        self.assertNotIn("Besoins recensés ?", rendered_labels)
        self.assertNotIn("Plusieurs usages", rendered_labels)

    def test_objective_page_has_no_treatment_or_effect_question(self):
        app = AppTest.from_file("app.py", default_timeout=10)
        app.session_state["screen"] = "objective"
        app.session_state["answers"] = self.ANSWERS
        app.session_state["result"] = None
        app.session_state["return_to_review"] = False
        app.run()

        self.assertEqual(len(app.exception), 0)
        labels = [selectbox.label for selectbox in app.selectbox]
        rendered_labels = " ".join(labels)
        self.assertNotIn("traiter vos contenus", rendered_labels)
        self.assertNotIn("effet principal", rendered_labels)

    def test_target_page_asks_one_usage_per_selected_network(self):
        app = AppTest.from_file("app.py", default_timeout=10)
        app.session_state["screen"] = "target"
        app.session_state["answers"] = self.ANSWERS
        app.session_state["result"] = None
        app.session_state["return_to_review"] = False
        app.run()

        labels = [selectbox.label for selectbox in app.selectbox]
        self.assertIn(
            "Sur Instagram, comment ce persona recherche-t-il concrètement cette information ?",
            labels,
        )
        self.assertIn(
            "Sur TikTok, comment ce persona recherche-t-il concrètement cette information ?",
            labels,
        )


if __name__ == "__main__":
    unittest.main()
