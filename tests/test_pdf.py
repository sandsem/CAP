import unittest

from pdf_export import build_summary_pdf
from scoring import evaluate
from tests.test_scoring import base_answers, fake_research


class PdfTests(unittest.TestCase):
    def test_summary_pdf_is_generated(self):
        answers = base_answers()
        result = evaluate(answers)
        answers["cabinet_name"] = "Cabinet Foeco"
        answers["target_age_range"] = "35 à 44 ans"
        pdf = build_summary_pdf(answers, result)
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertGreater(len(pdf), 5000)

    def test_summary_pdf_with_feasibility_actions_is_generated(self):
        answers = base_answers()
        answers["q8"] = "Aucun temps disponible"
        result = evaluate(answers)
        self.assertTrue(result["launch_actions"])
        self.assertEqual(result["feasibility_label"], "Lancement à reporter")
        pdf = build_summary_pdf(answers, result)
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertGreater(len(pdf), 5000)

    def test_summary_pdf_with_external_sources_is_generated(self):
        answers = base_answers()
        research = fake_research({"Instagram": "fort"})
        research["sources"] = [{
            "platform": "Instagram",
            "title": "Exemple de contenu public",
            "url": "https://www.instagram.com/example/",
            "snippet": "Exemple",
            "domain": "instagram.com",
        }]
        result = evaluate(answers, research)
        pdf = build_summary_pdf(answers, result)
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertGreater(len(pdf), 5000)

    def test_summary_pdf_resists_extreme_free_text(self):
        answers = base_answers()
        answers.update({
            "q2": ["Autre"],
            "custom_profile": "P" * 20000,
            "priority_need": "B" * 20000,
            "custom_source_details": "S" * 20000,
        })
        result = evaluate(answers)
        pdf = build_summary_pdf(answers, result)
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertGreater(len(pdf), 5000)


if __name__ == "__main__":
    unittest.main()
