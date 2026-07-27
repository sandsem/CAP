import unittest

from streamlit.testing.v1 import AppTest


class AppSmokeTests(unittest.TestCase):
    VISIB_ANSWERS = {
        "q1": "Oui",
        "q2": [
            "Micro-entrepreneur",
            "Start-up",
            "Profession libérale / Freelance",
        ],
        "q3": "Oui",
        "q4": ["Instagram"],
        "q5": ["Expérience terrain", "Étude sectorielle"],
        "q6": "Acquisition",
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

    def test_home_and_prepare_render(self):
        app = AppTest.from_file("app.py", default_timeout=10).run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Commencer", [button.label for button in app.button])

        app.button(key="start").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Continuer", [button.label for button in app.button])

    def test_target_screen_renders_five_questions(self):
        app = AppTest.from_file("app.py", default_timeout=10).run()
        app.button(key="start").click().run()
        app.button(key="prepare_continue").click().run()
        self.assertEqual(len(app.exception), 0)
        self.assertEqual(len(app.radio), 2)
        self.assertEqual(len(app.pills), 3)

    def test_review_precedes_result(self):
        app = AppTest.from_file("app.py", default_timeout=10)
        app.session_state["screen"] = "review"
        app.session_state["answers"] = self.VISIB_ANSWERS
        app.session_state["result"] = None
        app.session_state["return_to_review"] = False
        app.run()

        self.assertEqual(len(app.exception), 0)
        self.assertIn("Récapitulatif", [header.value for header in app.header])
        app.button(key="forward_from_review").click().run()

        self.assertEqual(len(app.exception), 0)
        self.assertEqual(app.session_state["screen"], "result")
        self.assertEqual(app.session_state["result"]["winner"], "Instagram")


if __name__ == "__main__":
    unittest.main()
