import os
import re
from datetime import date, datetime
from django.conf import settings
from django.core.cache import cache
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
    Fetches up to 100 results (2 pages of 50 results each).
    Fast, reliable, free, no API key needed, high-resolution artwork.
    """
    anilist_type = "ANIME" if media_type == "anime" else "MANGA"
    gql_query = """
    query ($search: String, $type: MediaType, $page: Int) {
      Page(page: $page, perPage: 50) {
        pageInfo {
          hasNextPage
        }
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
    data = []
    for page_num in (1, 2):
        try:
            resp = requests.post(
                "https://graphql.anilist.co",
                json={"query": gql_query, "variables": {"search": query, "type": anilist_type, "page": page_num}},
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=6,
            )
            if resp.status_code == 200:
                p_data = resp.json().get("data", {}).get("Page", {})
                media_list = p_data.get("media", [])
                data.extend(media_list)
                if not p_data.get("pageInfo", {}).get("hasNextPage", False):
                    break
            else:
                break
        except Exception:
            break

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
    """Fallback search using Kitsu API (up to 20 results)."""
    endpoint = "anime" if media_type == "anime" else "manga"
    url = f"https://kitsu.io/api/edge/{endpoint}"
    resp = requests.get(
        url,
        params={"filter[text]": query, "page[limit]": 20},
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
    """Secondary fallback search using Jikan (MyAnimeList, up to 25 results)."""
    url = f"https://api.jikan.moe/v4/{media_type}"
    resp = requests.get(url, params={"q": query, "limit": 25}, timeout=4.5)
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
    Modern keyless movie search combining IMDb (Hollywood, world cinema, blockbusters)
    and AniList (anime feature films).
    Replaces outdated TVMaze with up-to-date cinema records and high-res Amazon/IMDb posters.
    """
    results = []
    seen_ids = set()

    # 1. IMDb Modern Suggestion Search (Keyless, covers all Hollywood & world cinema)
    try:
        q_clean = re.sub(r'[^a-zA-Z0-9\s]', '', query).strip().lower()
        q_slug = re.sub(r'\s+', '_', q_clean)
        if q_slug:
            first_char = q_slug[0]
            url = f"https://v3.sg.media-imdb.com/suggestion/{first_char}/{q_slug}.json"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/json",
            }
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                for item in resp.json().get("d", []):
                    qid = str(item.get("id", ""))
                    if not qid.startswith("tt"):
                        continue
                    if qid in seen_ids:
                        continue
                    seen_ids.add(qid)

                    title = item.get("l") or ""
                    year = item.get("y")
                    qtype = item.get("q") or "movie"
                    stars = item.get("s") or ""
                    img = item.get("i", {}).get("imageUrl") or ""

                    release_date = date(year, 1, 1) if year else None
                    desc = f"Starring: {stars} • Released: {year}" if stars and year else (f"Released: {year}" if year else "Feature Film")

                    results.append({
                        "external_id": f"imdb_{qid}",
                        "media_type": "movie",
                        "media_title": title,
                        "media_description": desc,
                        "media_image": img,
                        "media_release_date": release_date,
                        "media_rate": None,
                        "genre": ["Movie", qtype.replace("_", " ").title()],
                    })
    except Exception:
        pass

    # 2. AniList Anime Movies
    try:
        gql_query = """
        query ($search: String) {
          Page(page: 1, perPage: 30) {
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
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {}).get("Page", {}).get("media", [])
            for item in data:
                aid = f"al_{item.get('id')}"
                if aid in seen_ids:
                    continue
                seen_ids.add(aid)

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
                    "external_id": aid,
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

    return results[:50]


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
        for item in data[:30]:
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
    """Search Open Library for novels and books (up to 50 results)."""
    resp = requests.get(
        "https://openlibrary.org/search.json",
        params={"q": query, "limit": 50},
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


def search_local_catalog(query, media_type):
    """Fallback search using titles already stored in media_catalog."""
    try:
        from apps.media_catalog.models import Media
        matches = Media.objects.filter(
            media_type__iexact=media_type,
            media_title__icontains=query
        )[:50]
        results = []
        for m in matches:
            results.append({
                "external_id": str(m.external_id),
                "media_type": m.media_type,
                "media_title": m.media_title,
                "media_description": m.media_description,
                "media_image": m.media_image,
                "media_release_date": m.media_release_date,
                "media_rate": float(m.media_rate) if m.media_rate is not None else None,
                "genre": m.genre or [],
            })
        return results
    except Exception:
        return []


def search_media(query, media_type):
    """
    Search with in-memory caching and expanded pagination (up to 100 results).
    When multiple users search at once for the same query, only the first request
    hits the external API. Subsequent requests are served directly from cache in ~1ms
    with zero rate limit consumption.
    """
    q = (query or "").strip().lower()
    mtype = (media_type or "").strip().lower()
    if not q:
        return []

    cache_key = f"renote:search:{mtype}:{re.sub(r'\\s+', '_', q)}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    results = []
    try:
        if mtype in ("anime", "manga"):
            try:
                results = search_anilist(q, mtype)
            except Exception as e:
                try:
                    results = search_kitsu(q, mtype)
                except Exception:
                    try:
                        results = search_jikan(q, mtype)
                    except Exception:
                        raise e
        elif mtype == "movie":
            results = search_tmdb(q)
        elif mtype == "novel":
            results = search_open_library(q)

        # Cache valid results for 30 minutes; empty results for 60s
        ttl = 1800 if results else 60
        cache.set(cache_key, results, timeout=ttl)
        return results

    except Exception as e:
        # If external API fails (rate limits 429, outages, timeouts),
        # fall back to titles already saved in media_catalog
        local_results = search_local_catalog(q, mtype)
        if local_results:
            cache.set(cache_key, local_results, timeout=300)
            return local_results
        raise e
