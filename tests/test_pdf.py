import unittest

from pdf_export import build_summary_pdf
from scoring import evaluate
from tests.test_scoring import base_answers


class PdfTests(unittest.TestCase):
    def test_summary_pdf_is_generated(self):
        answers = base_answers()
        result = evaluate(answers)
        pdf = build_summary_pdf(answers, result)
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertGreater(len(pdf), 3000)

    def test_summary_pdf_with_actions_is_generated(self):
        answers = base_answers()
        answers["q8"] = "Aucun temps disponible"
        result = evaluate(answers)
        self.assertTrue(result["launch_actions"])
        pdf = build_summary_pdf(answers, result)
        self.assertTrue(pdf.startswith(b"%PDF-"))
        self.assertGreater(len(pdf), 3000)

if __name__ == "__main__":
    unittest.main()
