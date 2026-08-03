"""Recherche documentaire publique utilisée par CAP.

CAP ne recherche ni personnes, ni coordonnées, ni prospects. Le module utilise
une API de recherche documentée lorsqu'une clé est configurée dans Streamlit
Cloud ou dans l'environnement. Sans clé, la recommandation reste disponible à
partir des réponses du cabinet et du référentiel CAP.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import os
import re
import time
import unicodedata
from urllib.parse import urlparse

import requests

from config import PLATFORM_NAMES

TAVILY_ENDPOINT = "https://api.tavily.com/search"
REQUEST_TIMEOUT = 10.0
MAX_RESULTS_PER_PLATFORM = 6

OFFICIAL_DOMAINS = {
    "Facebook": {"facebook.com", "about.fb.com", "meta.com"},
    "Instagram": {"instagram.com", "about.instagram.com", "creators.instagram.com", "meta.com"},
    "TikTok": {"tiktok.com", "newsroom.tiktok.com", "support.tiktok.com"},
    "YouTube": {"youtube.com", "blog.youtube", "support.google.com", "developers.google.com"},
}
AUTHORITATIVE_STUDY_DOMAINS = {
    "datareportal.com", "pewresearch.org", "ofcom.org.uk", "arcep.fr",
    "mediametrie.fr", "insee.fr", "eurostat.ec.europa.eu", "cnil.fr",
    "oecd.org", "ec.europa.eu", "statista.com",
}


@dataclass(frozen=True)
class PublicSource:
    title: str
    url: str
    snippet: str
    domain: str
    platform: str
    source_type: str
    authority: str
    published_date: str = ""
    relevance: str = "pertinente"
    quality_score: float = 0.0


def _contains_sensitive_pattern(value: str) -> bool:
    text = str(value or "")
    return bool(
        re.search(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b", text)
        or re.search(r"(?<!\d)(?:\+?\d[ .-]?){9,14}(?!\d)", text)
        or re.search(r"\b(?:siren|siret|n[°o]?\s*client|dossier(?:\s+client)?)\s*[:#-]?\s*\d{5,}\b", text, re.I)
    )


def _truncate_words(value: str, limit: int) -> str:
    value = str(value or "").strip()
    if len(value) <= limit:
        return value
    shortened = value[:limit].rsplit(" ", 1)[0].strip()
    return shortened or value[:limit]


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
        "facebook", "instagram", "tiktok", "youtube", "objectif", "cabinet",
    }
    return {
        token for token in re.findall(r"[a-z0-9]{3,}", _normalise(text))
        if token not in stopwords
    }


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def _domain_matches(domain: str, candidates: set[str]) -> bool:
    return any(domain == candidate or domain.endswith(f".{candidate}") for candidate in candidates)


def _classify_source(platform: str, domain: str) -> tuple[str, str]:
    if _domain_matches(domain, OFFICIAL_DOMAINS[platform]):
        return "source officielle", "élevée"
    if _domain_matches(domain, AUTHORITATIVE_STUDY_DOMAINS):
        return "étude ou organisme reconnu", "élevée"
    return "contenu public indexé", "complémentaire"


def _sanitise_term(value: str, limit: int) -> str:
    value = re.sub(r"[\r\n\t]+", " ", str(value or ""))
    value = re.sub(r"\S+@\S+", "", value)
    value = re.sub(r"\b(?:\+?\d[\d .-]{7,}\d)\b", "", value)
    return re.sub(r"\s+", " ", value).strip()[:limit]


def _query_for(platform: str, profile: str, need: str, objective: str, age_range: str = "") -> str:
    profile = _truncate_words(profile, 70)
    need = _truncate_words(need, 140)
    objective = _truncate_words(objective, 90)
    age_range = _truncate_words(age_range, 35)
    age_term = f' "{age_range}"' if age_range and age_range != "Je ne sais pas" else ""
    return (
        f'{platform} usages professionnels France 2025 2026 "{profile}" '
        f'"{need}" "{objective}"{age_term} étude audience formats contenus documentation officielle'
    )


def _tavily_search(api_key: str, query: str) -> list[dict]:
    payload = {
        "query": query,
        "search_depth": "advanced",
        "chunks_per_source": 2,
        "topic": "general",
        "country": "france",
        "time_range": "year",
        "max_results": MAX_RESULTS_PER_PLATFORM,
        "include_answer": False,
        "include_raw_content": False,
        "include_usage": True,
    }
    response = None
    for attempt in range(2):
        response = requests.post(
            TAVILY_ENDPOINT,
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code not in {429, 500, 502, 503, 504} or attempt == 1:
            break
        time.sleep(0.35)
    assert response is not None
    response.raise_for_status()
    body = response.json()
    results = body.get("results", [])
    if not isinstance(results, list):
        raise ValueError("Réponse de recherche invalide")
    return results


def _qualify_results(platform: str, results: list[dict], context: str) -> tuple[list[PublicSource], int]:
    context_tokens = _tokens(context)
    selected: list[PublicSource] = []
    seen: set[str] = set()
    raw_count = 0
    for item in results:
        url = str(item.get("url", "")).strip()
        title = str(item.get("title", "")).strip()
        snippet = str(item.get("content", item.get("snippet", ""))).strip()
        if not url or not title or url in seen:
            continue
        raw_count += 1
        domain = _domain(url)
        source_type, authority = _classify_source(platform, domain)
        source_tokens = _tokens(f"{title} {snippet}")
        overlap = len(context_tokens.intersection(source_tokens))
        try:
            api_score = max(0.0, min(float(item.get("score") or 0), 1.0))
        except (TypeError, ValueError):
            api_score = 0.0
        official_or_study = authority == "élevée"
        if official_or_study:
            qualified = overlap >= 1 or api_score >= 0.65
        else:
            qualified = overlap >= 2 and api_score >= 0.45
        if not qualified:
            continue
        published_date = str(item.get("published_date") or item.get("date") or "")[:30]
        recent_marker = bool(re.search(r"\b202[5-9]\b", f"{published_date} {title} {snippet}"))
        quality_score = round(
            (2.0 if official_or_study else 0.5)
            + min(overlap, 3)
            + (2.0 * api_score)
            + (1.0 if recent_marker else 0.0),
            2,
        )
        relevance = "forte" if quality_score >= 5.0 else "pertinente"
        selected.append(PublicSource(
            title=title[:180],
            url=url,
            snippet=snippet[:420],
            domain=domain,
            platform=platform,
            source_type=source_type,
            authority=authority,
            published_date=published_date,
            relevance=relevance,
            quality_score=quality_score,
        ))
        seen.add(url)
    return selected[:4], raw_count


def _signal_label(sources: list[PublicSource]) -> str:
    """Qualifie la solidité documentaire, pas la popularité de la plateforme."""
    scores = sorted((source.quality_score for source in sources), reverse=True)
    if not scores:
        return "faible"
    if scores[0] >= 5.5 or sum(scores[:2]) >= 9.0:
        return "fort"
    if scores[0] >= 3.5 or sum(scores[:2]) >= 6.0:
        return "modéré"
    return "faible"


def _empty_result(
    status: str,
    note: str,
    searched_at: str,
    error: str | None = None,
    provider: str = "Non configuré",
) -> dict:
    return {
        "status": status,
        "can_influence": False,
        "searched_at": searched_at,
        "provider": provider,
        "platforms": {
            platform: {"signal": "indisponible", "result_count": 0, "raw_count": 0, "sources": []}
            for platform in PLATFORM_NAMES
        },
        "sources": [],
        "note": note,
        "errors": [error] if error else [],
    }


def research_platforms(answers: dict, api_key: str | None = None) -> dict:
    """Recherche des informations publiques comparables pour les quatre plateformes.

    Seul l'état ``complet`` peut modifier la recommandation. Les états partiel,
    insuffisant et indisponible sont restitués à titre informatif.
    """
    searched_at = datetime.now(timezone.utc).astimezone().strftime("%d/%m/%Y %H:%M")
    api_key = (api_key or os.getenv("TAVILY_API_KEY", "")).strip()
    if not api_key:
        return _empty_result(
            "indisponible",
            "La recherche externe n’est pas configurée. CAP utilise les données du cabinet et son référentiel interne.",
            searched_at,
        )

    raw_profile = (answers.get("q2") or [""])[0]
    if raw_profile == "Autre":
        raw_profile = answers.get("custom_profile", "") or "persona professionnel"
    raw_need = answers.get("priority_need", "")
    raw_objective = answers.get("custom_objective") if answers.get("q6") == "Autre" else answers.get("q6", "")
    if any(_contains_sensitive_pattern(value) for value in (raw_profile, raw_need, raw_objective)):
        return _empty_result(
            "indisponible",
            "La recherche externe n’a pas été exécutée : les champs doivent être anonymisés avant tout envoi.",
            searched_at,
            provider="Tavily (non appelé)",
        )
    profile = _sanitise_term(raw_profile, 100)
    need = _sanitise_term(raw_need, 240)
    objective = _sanitise_term(raw_objective, 160)
    age_range = _sanitise_term(answers.get("target_age_range", ""), 40)
    context = f"{profile} {need} {objective} {age_range}"

    platform_data: dict[str, dict] = {}
    errors: list[str] = []
    all_sources: list[dict] = []

    def run(platform: str) -> tuple[str, dict]:
        query = _query_for(platform, profile, need, objective, age_range)
        results = _tavily_search(api_key, query)
        sources, raw_count = _qualify_results(platform, results, context)
        return platform, {
            "signal": _signal_label(sources),
            "result_count": len(sources),
            "raw_count": raw_count,
            "sources": [asdict(source) for source in sources],
        }

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(run, platform): platform for platform in PLATFORM_NAMES}
        for future in as_completed(futures):
            platform = futures[future]
            try:
                name, data = future.result()
                platform_data[name] = data
            except (requests.RequestException, ValueError, TypeError) as exc:
                errors.append(f"{platform}: {exc.__class__.__name__}")
                platform_data[platform] = {
                    "signal": "indisponible", "result_count": 0, "raw_count": 0, "sources": []
                }

    for platform in PLATFORM_NAMES:
        platform_data.setdefault(platform, {
            "signal": "indisponible", "result_count": 0, "raw_count": 0, "sources": []
        })
        for source in platform_data[platform]["sources"][:2]:
            if source["url"] not in {item["url"] for item in all_sources}:
                all_sources.append(source)

    available = [p for p, data in platform_data.items() if data["signal"] != "indisponible"]
    qualified = [p for p, data in platform_data.items() if data["result_count"] > 0]
    if not available:
        status = "indisponible"
        note = "La recherche publique n’a pas pu être exécutée. CAP utilise les données du cabinet et son référentiel interne."
    elif len(available) < len(PLATFORM_NAMES):
        status = "partiel"
        note = "La couverture n’est pas comparable entre les quatre plateformes. Les résultats sont informatifs et ne modifient pas la recommandation."
    elif len(qualified) < len(PLATFORM_NAMES):
        status = "insuffisant"
        note = "La recherche a abouti, mais les sources qualifiées sont insuffisantes pour comparer équitablement les quatre plateformes."
    else:
        status = "complet"
        note = "Les quatre plateformes disposent de sources publiques qualifiées et comparables. Ce signal complète, sans remplacer, les données du cabinet."

    can_influence = status == "complet"
    return {
        "status": status,
        "can_influence": can_influence,
        "searched_at": searched_at,
        "provider": "Tavily",
        "platforms": platform_data,
        "sources": all_sources[:8],
        "note": note,
        "errors": errors,
    }
