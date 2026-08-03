import unittest
from pathlib import Path

try:
    from streamlit.testing.v1 import AppTest
except ModuleNotFoundError:
    AppTest = None

from tests.test_scoring import base_answers


class InterfaceRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = Path("app.py").read_text(encoding="utf-8")
        cls.pdf_source = Path("pdf_export.py").read_text(encoding="utf-8")

    def test_native_enter_instruction_is_hidden(self):
        self.assertIn('[data-testid*="InputInstructions"]', self.source)
        self.assertIn("display:none!important", self.source)

    def test_dropdown_options_are_forced_to_dark_background(self):
        self.assertIn('div[data-baseweb="popover"]', self.source)
        self.assertIn('[role="option"]', self.source)
        self.assertIn("background:#111!important", self.source)

    def test_out_of_scope_option_explicitly_names_the_four_networks(self):
        from config import OUT_OF_SCOPE_NETWORK

        for network in ("Facebook", "Instagram", "TikTok", "YouTube"):
            self.assertIn(network, OUT_OF_SCOPE_NETWORK)

    def test_responsible_options_include_other(self):
        from config import PILOT_OPTIONS

        self.assertIn("Autre", PILOT_OPTIONS)

    def test_all_observed_networks_are_displayed_in_review(self):
        self.assertIn('("Réseaux observés :",', self.source)

    def test_external_research_runs_inside_analysis_without_new_screen(self):
        self.assertIn("cached_external_research", self.source)
        self.assertIn("research_platforms", self.source)
        self.assertNotIn('"research":', self.source)

    def test_manual_tie_choice_is_removed(self):
        self.assertNotIn("Quelle plateforme le cabinet retient-il", self.source)
        self.assertNotIn("retain_", self.source)

    def test_feasibility_remains_in_pdf(self):
        self.assertIn("Contrôle de la faisabilité", self.pdf_source)
        self.assertIn("feasibility_label", self.pdf_source)

    def test_reference_base_is_not_announced_in_the_questionnaire(self):
        self.assertNotIn("CAP utilisera sa base de référence", self.source)


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

    def test_target_has_no_detailed_behaviour_study(self):
        app = self._app("target", base_answers())
        self.assertEqual(len(app.exception), 0)
        labels = [item.label for item in list(app.radio) + list(app.selectbox) + list(app.text_input)]
        text = " ".join(labels)
        self.assertNotIn("comment ce persona recherche", text.lower())
        self.assertNotIn("fréquence d’utilisation", text.lower())

    def test_undefined_persona_stops_the_target_step(self):
        answers = base_answers()
        answers["q1"] = "Non"
        app = self._app("target", answers)
        labels = [item.label for item in list(app.selectbox) + list(app.text_input)]
        self.assertEqual(labels, [])
        self.assertNotIn("Continuer", [button.label for button in app.button])
        self.assertIn(
            "Finalisez le persona avant de continuer.",
            [item.value for item in app.error],
        )

    def test_objective_non_defined_hides_smart_fields(self):
        answers = base_answers()
        answers["q6"] = "Non défini"
        app = self._app("objective", answers)
        labels = [item.label for item in list(app.selectbox) + list(app.text_input)]
        self.assertNotIn("Indicateur suivi", labels)
        self.assertNotIn("Résultat attendu", labels)

    def test_acquisition_does_not_offer_recruitment_indicators(self):
        app = self._app("objective", base_answers())
        indicator = next(item for item in app.selectbox if item.label == "Indicateur suivi")
        self.assertNotIn("Candidatures reçues", indicator.options)
        self.assertIn("Demandes de contact", indicator.options)

    def test_resources_does_not_reveal_a_platform(self):
        app = self._app("resources", base_answers())
        rendered = " ".join(item.value for item in app.markdown if hasattr(item, "value"))
        self.assertNotIn("Instagram est", rendered)
        self.assertNotIn("TikTok est", rendered)

    def test_resources_allows_several_responsible_people(self):
        app = self._app("resources", base_answers())
        self.assertIn("Qui pilotera la communication ?", [item.label for item in app.multiselect])

    def test_resources_allows_another_responsible_person(self):
        answers = base_answers()
        answers.update({"q11": ["Autre"], "custom_pilot": "La secrétaire du cabinet"})
        app = self._app("resources", answers)
        self.assertIn("Précisez l’autre responsable", [item.label for item in app.text_input])

    def test_review_has_no_previous_button(self):
        app = self._app("review", base_answers())
        self.assertNotIn("Précédent", [button.label for button in app.button])


if __name__ == "__main__":
    unittest.main()
