import os
import re
from datetime import date, datetime
from django.conf import settings
import requests


def _clean_html(text):
    """Strip HTML tags from synopses/descriptions."""
    if not text:
        return ""
    clean = re.sub(r"<[^>]+>", "", text)
    return clean.replace("\n", " ").strip()


def _parse_date(date_str):
    """Best-effort parse of various date string formats into a date object."""
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S%z", "%Y"):
        try:
            return datetime.strptime(
                date_str[: len(fmt.replace("%", "").replace("z", ""))] if fmt == "%Y" else date_str,
                fmt,
            ).date()
        except (ValueError, TypeError):
            continue
    return None


def search_anilist(query, media_type):
    """
    Search AniList GraphQL API for anime or manga.
    Fast, reliable, free, no API key needed, high-resolution artwork.
    """
    anilist_type = "ANIME" if media_type == "anime" else "MANGA"
    gql_query = """
    query ($search: String, $type: MediaType) {
      Page(page: 1, perPage: 12) {
        media(search: $search, type: $type, sort: POPULARITY_DESC) {
          id
          title {
            english
            romaji
            native
          }
          description
          coverImage {
            large
            extraLarge
          }
          startDate {
            year
            month
            day
          }
          averageScore
          genres
        }
      }
    }
    """
    resp = requests.post(
        "https://graphql.anilist.co",
        json={"query": gql_query, "variables": {"search": query, "type": anilist_type}},
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        timeout=5,
    )
    resp.raise_for_status()
    data = resp.json().get("data", {}).get("Page", {}).get("media", [])

    results = []
    for item in data:
        titles = item.get("title") or {}
        media_title = titles.get("english") or titles.get("romaji") or titles.get("native") or ""

        start = item.get("startDate") or {}
        release_date = None
        if start.get("year"):
            try:
                release_date = date(
                    start["year"],
                    start.get("month") or 1,
                    start.get("day") or 1,
                )
            except ValueError:
                pass

        score = item.get("averageScore")
        media_rate = round(score / 10.0, 1) if score is not None else None

        cover = item.get("coverImage") or {}
        img_url = cover.get("extraLarge") or cover.get("large") or ""

        results.append({
            "external_id": str(item.get("id")),
            "media_type": media_type,
            "media_title": media_title,
            "media_description": _clean_html(item.get("description")),
            "media_image": img_url,
            "media_release_date": release_date,
            "media_rate": media_rate,
            "genre": item.get("genres", []),
        })

    return results


def search_kitsu(query, media_type):
    """Fallback search using Kitsu API."""
    endpoint = "anime" if media_type == "anime" else "manga"
    url = f"https://kitsu.io/api/edge/{endpoint}"
    resp = requests.get(
        url,
        params={"filter[text]": query, "page[limit]": 12},
        headers={"Accept": "application/vnd.api+json"},
        timeout=6,
    )
    resp.raise_for_status()
    data = resp.json().get("data", [])

    results = []
    for item in data:
        attrs = item.get("attributes", {})
        titles = attrs.get("titles", {})
        media_title = (
            attrs.get("canonicalTitle")
            or titles.get("en")
            or titles.get("en_jp")
            or titles.get("ja_jp")
            or ""
        )
        poster_img = attrs.get("posterImage", {})
        img_url = poster_img.get("large") or poster_img.get("medium") or ""

        release_date = None
        start_date = attrs.get("startDate")
        if start_date:
            try:
                release_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            except ValueError:
                pass

        rating = attrs.get("averageRating")
        media_rate = round(float(rating) / 10.0, 1) if rating else None

        results.append({
            "external_id": str(item.get("id")),
            "media_type": media_type,
            "media_title": media_title,
            "media_description": _clean_html(attrs.get("synopsis")),
            "media_image": img_url,
            "media_release_date": release_date,
            "media_rate": media_rate,
            "genre": [],
        })
    return results


def search_jikan(query, media_type):
    """Secondary fallback search using Jikan (MyAnimeList)."""
    url = f"https://api.jikan.moe/v4/{media_type}"
    resp = requests.get(url, params={"q": query, "limit": 12}, timeout=3.5)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    results = []
    for item in data:
        results.append({
            "external_id": str(item.get("mal_id")),
            "media_type": media_type,
            "media_title": item.get("title") or "",
            "media_description": _clean_html(item.get("synopsis")),
            "media_image": (item.get("images", {}).get("jpg", {}).get("large_image_url") or ""),
            "media_release_date": _parse_date((item.get("aired") or item.get("published") or {}).get("from")),
            "media_rate": item.get("score"),
            "genre": [g["name"] for g in item.get("genres", [])],
        })
    return results


def search_free_movies(query):
    """
    Keyless movie search combining TVMaze (popular movies/shows)
    and AniList (anime movies).
    """
    results = []

    # 1. TVMaze
    try:
        url = "https://api.tvmaze.com/search/shows"
        resp = requests.get(url, params={"q": query}, timeout=5)
        if resp.status_code == 200:
            for entry in resp.json():
                show = entry.get("show") or {}
                image = (show.get("image") or {}).get("original") or (show.get("image") or {}).get("medium") or ""
                release_date = None
                if show.get("premiered"):
                    try:
                        release_date = datetime.strptime(show["premiered"], "%Y-%m-%d").date()
                    except ValueError:
                        pass
                results.append({
                    "external_id": f"tv_{show.get('id')}",
                    "media_type": "movie",
                    "media_title": show.get("name") or "",
                    "media_description": _clean_html(show.get("summary")),
                    "media_image": image,
                    "media_release_date": release_date,
                    "media_rate": (show.get("rating") or {}).get("average"),
                    "genre": show.get("genres", []),
                })
    except Exception:
        pass

    # 2. AniList Anime Movies
    try:
        gql_query = """
        query ($search: String) {
          Page(page: 1, perPage: 8) {
            media(search: $search, type: ANIME, format: MOVIE, sort: POPULARITY_DESC) {
              id
              title { english romaji native }
              description
              coverImage { large extraLarge }
              startDate { year month day }
              averageScore
              genres
            }
          }
        }
        """
        resp = requests.post(
            "https://graphql.anilist.co",
            json={"query": gql_query, "variables": {"search": query}},
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=4,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {}).get("Page", {}).get("media", [])
            for item in data:
                titles = item.get("title") or {}
                media_title = titles.get("english") or titles.get("romaji") or titles.get("native") or ""
                start = item.get("startDate") or {}
                release_date = None
                if start.get("year"):
                    try:
                        release_date = date(start["year"], start.get("month") or 1, start.get("day") or 1)
                    except ValueError:
                        pass
                score = item.get("averageScore")
                media_rate = round(score / 10.0, 1) if score is not None else None
                cover = item.get("coverImage") or {}
                img_url = cover.get("extraLarge") or cover.get("large") or ""
                results.append({
                    "external_id": f"al_{item.get('id')}",
                    "media_type": "movie",
                    "media_title": media_title,
                    "media_description": _clean_html(item.get("description")),
                    "media_image": img_url,
                    "media_release_date": release_date,
                    "media_rate": media_rate,
                    "genre": item.get("genres", []),
                })
    except Exception:
        pass

    return results[:12]


def search_tmdb(query):
    """Search TMDB if API key is configured; otherwise fallback to keyless search."""
    api_key = getattr(settings, "TMDB_API_KEY", os.environ.get("TMDB_API_KEY", "")).strip()

    if not api_key:
        return search_free_movies(query)

    try:
        resp = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={"api_key": api_key, "query": query},
            timeout=6,
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
                "media_description": _clean_html(item.get("overview")),
                "media_image": f"https://image.tmdb.org/t/p/w500{poster}" if poster else "",
                "media_release_date": _parse_date(item.get("release_date")),
                "media_rate": item.get("vote_average"),
                "genre": [],
            })
        return results if results else search_free_movies(query)
    except Exception:
        return search_free_movies(query)


def search_open_library(query):
    resp = requests.get(
        "https://openlibrary.org/search.json",
        params={"q": query, "limit": 12},
        timeout=8,
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
            "media_description": "",
            "media_image": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else "",
            "media_release_date": _parse_date(str(year)) if year else None,
            "media_rate": None,
            "genre": item.get("subject", [])[:5] if item.get("subject") else [],
        })
    return results


def search_media(query, media_type):
    if media_type in ("anime", "manga"):
        try:
            return search_anilist(query, media_type)
        except Exception as e:
            try:
                return search_kitsu(query, media_type)
            except Exception:
                try:
                    return search_jikan(query, media_type)
                except Exception:
                    raise e
    elif media_type == "movie":
        return search_tmdb(query)
    elif media_type == "novel":
        return search_open_library(query)
    return []
