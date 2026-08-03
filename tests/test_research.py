import unittest
from unittest.mock import patch

import requests

from research import PublicSource, research_platforms
from tests.test_scoring import base_answers


class ResearchTests(unittest.TestCase):
    @patch("research._search")
    def test_live_public_research_is_structured(self, mocked_search):
        mocked_search.return_value = [
            PublicSource(
                title="Choisir son statut juridique",
                url="https://www.youtube.com/watch?v=example",
                snippet="Micro-entrepreneur et société : les étapes",
                domain="youtube.com",
            )
        ]
        result = research_platforms(base_answers())
        self.assertEqual(result["status"], "live")
        self.assertEqual(set(result["platforms"]), {"Facebook", "Instagram", "TikTok", "YouTube"})
        self.assertTrue(result["sources"])

    @patch("research._search", side_effect=requests.RequestException("offline"))
    def test_search_failure_uses_transparent_fallback(self, _mocked_search):
        result = research_platforms(base_answers())
        self.assertEqual(result["status"], "fallback")
        self.assertIn("référentiel interne", result["note"])
        self.assertTrue(result["errors"])


if __name__ == "__main__":
    unittest.main()
