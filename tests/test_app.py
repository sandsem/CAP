import unittest

from streamlit.testing.v1 import AppTest


class AppSmokeTests(unittest.TestCase):
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
        self.assertEqual(len(app.multiselect), 3)


if __name__ == "__main__":
    unittest.main()
