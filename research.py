"""Recherche documentaire publique utilisée par CAP.

Le module ne collecte ni coordonnées ni données personnelles. Il recherche des
pages publiques indexées afin d'apporter des signaux récents au moteur de
comparaison. En cas d'indisponibilité du moteur de recherche, CAP bascule de
manière transparente sur son référentiel interne.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from html import unescape
import re
import unicodedata
from urllib.parse import parse_qs, unquote, urlparse

import requests
from bs4 import BeautifulSoup

from config import PLATFORM_NAMES


SEARCH_ENDPOINT = "https://html.duckduckgo.com/html/"
LITE_SEARCH_ENDPOINT = "https://lite.duckduckgo.com/lite/"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
)
PLATFORM_DOMAINS = {
    "Facebook": "facebook.com",
    "Instagram": "instagram.com",
    "TikTok": "tiktok.com",
    "YouTube": "youtube.com",
}


@dataclass(frozen=True)
class PublicSource:
    title: str
    url: str
    snippet: str
    domain: str


def _normalise(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text.lower()).strip()


def _tokens(text: str) -> set[str]:
    stopwords = {
        "avec", "dans", "pour", "sans", "chez", "cette", "entre", "vers", "plus",
        "moins", "comment", "quel", "quelle", "quels", "quelles", "une", "des", "les",
        "leur", "leurs", "son", "ses", "sur", "par", "qui", "que", "quoi", "dont",
        "persona", "information", "besoin", "prioritaire", "expert", "comptable",
    }
    return {
        token for token in re.findall(r"[a-z0-9]{3,}", _normalise(text))
        if token not in stopwords
    }


def _clean_redirect_url(url: str) -> str:
    if not url:
        return ""
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    if "uddg" in query:
        return unquote(query["uddg"][0])
    return url


def _parse_search_page(html: str, max_results: int) -> list[PublicSource]:
    soup = BeautifulSoup(html, "html.parser")
    sources: list[PublicSource] = []
    seen: set[str] = set()

    for result in soup.select(".result"):
        link = result.select_one("a.result__a")
        if link is None:
            continue
        url = _clean_redirect_url(link.get("href", ""))
        if not url or url in seen:
            continue
        title = unescape(link.get_text(" ", strip=True))
        snippet_node = result.select_one(".result__snippet")
        snippet = unescape(snippet_node.get_text(" ", strip=True)) if snippet_node else ""
        domain = urlparse(url).netloc.lower().removeprefix("www.")
        sources.append(PublicSource(title=title, url=url, snippet=snippet, domain=domain))
        seen.add(url)
        if len(sources) >= max_results:
            return sources

    # Structure de repli de la version légère du moteur de recherche.
    for link in soup.select("a.result-link"):
        url = _clean_redirect_url(link.get("href", ""))
        if not url or url in seen:
            continue
        title = unescape(link.get_text(" ", strip=True))
        row = link.find_parent("tr")
        snippet = ""
        if row is not None:
            next_row = row.find_next_sibling("tr")
            if next_row is not None:
                snippet = unescape(next_row.get_text(" ", strip=True))
        domain = urlparse(url).netloc.lower().removeprefix("www.")
        sources.append(PublicSource(title=title, url=url, snippet=snippet, domain=domain))
        seen.add(url)
        if len(sources) >= max_results:
            break
    return sources


def _search(query: str, max_results: int = 6, timeout: float = 7.0) -> list[PublicSource]:
    response = requests.post(
        SEARCH_ENDPOINT,
        data={"q": query, "kl": "fr-fr"},
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
    )
    response.raise_for_status()
    sources = _parse_search_page(response.text, max_results)
    if sources:
        return sources

    fallback = requests.post(
        LITE_SEARCH_ENDPOINT,
        data={"q": query, "kl": "fr-fr"},
        headers={"User-Agent": USER_AGENT},
        timeout=timeout,
    )
    fallback.raise_for_status()
    return _parse_search_page(fallback.text, max_results)


def _relevant_sources(sources: list[PublicSource], context: str) -> list[PublicSource]:
    context_tokens = _tokens(context)
    if not context_tokens:
        return sources
    relevant: list[PublicSource] = []
    for source in sources:
        source_tokens = _tokens(f"{source.title} {source.snippet}")
        if context_tokens.intersection(source_tokens):
            relevant.append(source)
    return relevant


def _signal_label(count: int) -> str:
    if count >= 3:
        return "fort"
    if count >= 1:
        return "modéré"
    return "faible"


def research_platforms(answers: dict) -> dict:
    """Recherche des signaux publics pour les quatre plateformes.

    Le résultat est structuré pour être utilisable par le moteur, l'écran final
    et le PDF. Une panne réseau n'empêche jamais CAP de terminer le diagnostic.
    """
    profile = (answers.get("q2") or [""])[0]
    if profile == "Autre":
        profile = answers.get("custom_profile", "") or "persona professionnel"
    need = str(answers.get("priority_need", "")).strip()
    objective = str(answers.get("q6", "")).strip()
    context = f"{profile} {need} {objective}"
    searched_at = datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M")

    platform_data: dict[str, dict] = {}
    all_sources: list[dict] = []
    errors: list[str] = []

    for platform in PLATFORM_NAMES:
        domain = PLATFORM_DOMAINS[platform]
        query = f"site:{domain} {profile} {need}"
        try:
            raw_sources = _search(query)
            relevant = _relevant_sources(raw_sources, context)
            selected = relevant[:4]
            serialised = [asdict(source) for source in selected]
            platform_data[platform] = {
                "query": query,
                "signal": _signal_label(len(selected)),
                "result_count": len(selected),
                "sources": serialised,
            }
            for source in serialised[:2]:
                if source["url"] not in {item["url"] for item in all_sources}:
                    all_sources.append({"platform": platform, **source})
        except (requests.RequestException, ValueError) as exc:
            errors.append(f"{platform}: {exc.__class__.__name__}")
            platform_data[platform] = {
                "query": query,
                "signal": "indisponible",
                "result_count": 0,
                "sources": [],
            }

    live_platforms = [
        platform for platform, data in platform_data.items()
        if data["signal"] != "indisponible"
    ]
    status = "live" if live_platforms else "fallback"
    note = (
        "La recherche s'appuie sur des pages publiques indexées. Elle constitue un signal documentaire, "
        "et non une mesure exhaustive de l'audience de chaque plateforme."
        if status == "live"
        else "La recherche publique n'était pas disponible. CAP a terminé l'analyse avec son référentiel interne et les données du cabinet."
    )

    return {
        "status": status,
        "searched_at": searched_at,
        "context": context,
        "platforms": platform_data,
        "sources": all_sources[:8],
        "note": note,
        "errors": errors,
    }
