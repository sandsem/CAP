import unittest

try:
    from streamlit.testing.v1 import AppTest
except ModuleNotFoundError:
    AppTest = None

from tests.test_scoring import base_answers


@unittest.skipIf(AppTest is None, "Streamlit n’est pas installé dans cet environnement")
class AppSmokeTests(unittest.TestCase):
    def _app(self, screen, answers=None):
        app = AppTest.from_file("app.py", default_timeout=10)
        app.session_state["screen"] = screen
        app.session_state["answers"] = answers or {}
        app.session_state["result"] = None
        app.session_state["return_to_review"] = False
        return app.run()

    def test_home_renders(self):
        app = AppTest.from_file("app.py", default_timeout=10).run()
        self.assertEqual(len(app.exception), 0)
        self.assertIn("Commencer", [button.label for button in app.button])

    def test_target_has_no_platform_usage_questions(self):
        app = self._app("target", base_answers())
        self.assertEqual(len(app.exception), 0)
        labels = [item.label for item in list(app.radio) + list(app.selectbox) + list(app.text_input)]
        text = " ".join(labels)
        self.assertNotIn("comment ce persona recherche", text.lower())
        self.assertNotIn("usage observé", text.lower())

    def test_objective_non_defined_hides_smart_fields(self):
        answers = base_answers()
        answers["q6"] = "Non défini"
        app = self._app("objective", answers)
        labels = [item.label for item in list(app.selectbox) + list(app.text_input)]
        self.assertNotIn("Indicateur suivi", labels)
        self.assertNotIn("Résultat attendu", labels)

    def test_resources_does_not_reveal_a_platform(self):
        app = self._app("resources", base_answers())
        rendered = " ".join(item.value for item in app.markdown if hasattr(item, "value"))
        self.assertNotIn("Instagram est", rendered)
        self.assertNotIn("TikTok est", rendered)

    def test_review_has_no_previous_button(self):
        app = self._app("review", base_answers())
        self.assertNotIn("Précédent", [button.label for button in app.button])


if __name__ == "__main__":
    unittest.main()
