import unittest
from unittest.mock import patch

import requests

from research import _tavily_search, research_platforms
from tests.test_scoring import base_answers


def result_for(platform: str):
    domains = {
        "Facebook": "about.fb.com",
        "Instagram": "about.instagram.com",
        "TikTok": "newsroom.tiktok.com",
        "YouTube": "blog.youtube",
    }
    return [{
        "title": f"{platform} : usages et formats professionnels",
        "url": f"https://{domains[platform]}/example",
        "content": "création entreprise visibilité contenus professionnels étude 2026",
        "score": 0.9,
        "published_date": "2026-02-01",
    }]


class ResearchTests(unittest.TestCase):
    def test_missing_key_is_transparent_and_cannot_influence(self):
        result = research_platforms(base_answers(), api_key="")
        self.assertEqual(result["status"], "indisponible")
        self.assertFalse(result["can_influence"])
        self.assertIn("n’est pas configurée", result["note"])

    @patch("research._tavily_search")
    def test_complete_public_research_is_structured(self, mocked_search):
        mocked_search.side_effect = lambda _key, query: result_for(next(p for p in ("Facebook", "Instagram", "TikTok", "YouTube") if p in query))
        result = research_platforms(base_answers(), api_key="secret")
        self.assertEqual(result["status"], "complet")
        self.assertTrue(result["can_influence"])
        self.assertEqual(set(result["platforms"]), {"Facebook", "Instagram", "TikTok", "YouTube"})
        self.assertTrue(result["sources"])
        self.assertTrue(all(source["authority"] == "élevée" for source in result["sources"]))

    @patch("research._tavily_search")
    def test_empty_search_is_insufficient_and_neutral(self, mocked_search):
        mocked_search.return_value = []
        result = research_platforms(base_answers(), api_key="secret")
        self.assertEqual(result["status"], "insuffisant")
        self.assertFalse(result["can_influence"])

    @patch("research._tavily_search")
    def test_partial_search_is_neutral(self, mocked_search):
        def side_effect(_key, query):
            if "TikTok" in query:
                raise requests.RequestException("offline")
            platform = next(p for p in ("Facebook", "Instagram", "YouTube") if p in query)
            return result_for(platform)
        mocked_search.side_effect = side_effect
        result = research_platforms(base_answers(), api_key="secret")
        self.assertEqual(result["status"], "partiel")
        self.assertFalse(result["can_influence"])
        self.assertTrue(result["errors"])


    @patch("research._tavily_search")
    def test_optional_age_range_refines_queries(self, mocked_search):
        answers = base_answers()
        answers["target_age_range"] = "35 à 44 ans"
        mocked_search.side_effect = lambda _key, query: result_for(next(p for p in ("Facebook", "Instagram", "TikTok", "YouTube") if p in query))
        research_platforms(answers, api_key="secret")
        queries = [call.args[1] for call in mocked_search.call_args_list]
        self.assertTrue(queries)
        self.assertTrue(all("35 à 44 ans" in query for query in queries))

    @patch("research.requests.post")
    def test_tavily_uses_bearer_auth_and_no_key_in_payload(self, mocked_post):
        mocked_post.return_value.raise_for_status.return_value = None
        mocked_post.return_value.json.return_value = {"results": []}
        _tavily_search("tvly-secret", "requête")
        kwargs = mocked_post.call_args.kwargs
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer tvly-secret")
        self.assertNotIn("api_key", kwargs["json"])

    @patch("research._tavily_search")
    def test_unrelated_official_result_is_not_enough(self, mocked_search):
        mocked_search.return_value = [{
            "title": "Page officielle sans rapport",
            "url": "https://about.instagram.com/unrelated",
            "content": "musique divertissement international",
            "score": 0.2,
        }]
        result = research_platforms(base_answers(), api_key="secret")
        self.assertEqual(result["status"], "insuffisant")
        self.assertFalse(result["can_influence"])

    @patch("research._tavily_search")
    def test_sensitive_context_is_never_sent(self, mocked_search):
        answers = base_answers()
        answers["priority_need"] = "Écrire à contact@example.com"
        result = research_platforms(answers, api_key="secret")
        self.assertEqual(result["status"], "indisponible")
        mocked_search.assert_not_called()


if __name__ == "__main__":
    unittest.main()
