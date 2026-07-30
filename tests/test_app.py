import unittest

from streamlit.testing.v1 import AppTest


class AppSmokeTests(unittest.TestCase):
    ANSWERS = {
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
        ],
        "q11": "Expert-comptable",
        "q12": ["Aucun appui"],
        "q12_status": "Aucune aide nécessaire",
        "q13": "Budget validé",
        "q15": None,
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


if __name__ == "__main__":
    unittest.main()
