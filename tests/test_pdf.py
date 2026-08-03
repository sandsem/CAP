import unittest

from pdf_export import build_summary_pdf
from scoring import evaluate
from tests.test_scoring import base_answers, fake_research


class PdfTests(unittest.TestCase):
    def test_summary_pdf_is_generated(self):
        answers = base_answers()
        result = evaluate(answers)
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


if __name__ == "__main__":
    unittest.main()
