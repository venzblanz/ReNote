import requests
from datetime import datetime
from django.conf import settings


def _parse_date(date_str):
    """Best-effort parse of various date string formats into a date object."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z", "%Y"):
        try:
            return datetime.strptime(date_str[:len(fmt.replace('%', '').replace('z', ''))] if fmt == "%Y" else date_str, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def search_jikan(query, media_type):
    """media_type is 'anime' or 'manga'."""
    url = f"https://api.jikan.moe/v4/{media_type}"
    resp = requests.get(url, params={"q": query, "limit": 12}, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    results = []
    for item in data:
        results.append({
            "external_id": str(item.get("mal_id")),
            "media_type": media_type,
            "media_title": item.get("title") or "",
            "media_description": item.get("synopsis") or "",
            "media_image": (item.get("images", {}).get("jpg", {}).get("large_image_url") or ""),
            "media_release_date": _parse_date((item.get("aired") or item.get("published") or {}).get("from")),
            "media_rate": item.get("score"),
            "genre": [g["name"] for g in item.get("genres", [])],
        })
    return results


def search_tmdb(query):
    api_key = settings.TMDB_API_KEY
    resp = requests.get(
        "https://api.themoviedb.org/3/search/movie",
        params={"api_key": api_key, "query": query},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json().get("results", [])

    results = []
    for item in data[:12]:
        poster = item.get("poster_path")
        results.append({
            "external_id": str(item.get("id")),
            "media_type": "movie",
            "media_title": item.get("title") or "",
            "media_description": item.get("overview") or "",
            "media_image": f"https://image.tmdb.org/t/p/w500{poster}" if poster else "",
            "media_release_date": _parse_date(item.get("release_date")),
            "media_rate": item.get("vote_average"),
            "genre": [],  # TMDB search endpoint returns genre_ids, not names — needs a lookup, skip for now
        })
    return results


def search_open_library(query):
    resp = requests.get(
        "https://openlibrary.org/search.json",
        params={"q": query, "limit": 12},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json().get("docs", [])

    results = []
    for item in data:
        cover_id = item.get("cover_i")
        year = item.get("first_publish_year")
        results.append({
            "external_id": item.get("key") or "",
            "media_type": "novel",
            "media_title": item.get("title") or "",
            "media_description": "",  # Open Library's search endpoint doesn't return a description
            "media_image": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else "",
            "media_release_date": _parse_date(str(year)) if year else None,
            "media_rate": None,
            "genre": item.get("subject", [])[:5] if item.get("subject") else [],
        })
    return results


def search_media(query, media_type):
    if media_type in ("anime", "manga"):
        return search_jikan(query, media_type)
    elif media_type == "movie":
        return search_tmdb(query)
    elif media_type == "novel":
        return search_open_library(query)
    return []