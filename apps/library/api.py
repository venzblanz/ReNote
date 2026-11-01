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


def search_anilist(query, media_type, genre=None):
    """
    Search AniList GraphQL API for anime or manga with query and/or genre filter.
    Fetches up to 100 results (2 pages of 50 results each).
    When query is empty and genre is specified, returns top/popular titles for that genre.
    """
    anilist_type = "ANIME" if media_type == "anime" else "MANGA"
    gql_query = """
    query ($search: String, $type: MediaType, $genre: String, $page: Int) {
      Page(page: $page, perPage: 50) {
        pageInfo {
          hasNextPage
        }
        media(search: $search, type: $type, genre: $genre, sort: POPULARITY_DESC) {
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
    search_val = query.strip() if query and query.strip() else None
    genre_val = genre.strip() if genre and genre.strip().lower() != "all" else None

    for page_num in (1, 2):
        try:
            resp = requests.post(
                "https://graphql.anilist.co",
                json={
                    "query": gql_query,
                    "variables": {
                        "search": search_val,
                        "type": anilist_type,
                        "genre": genre_val,
                        "page": page_num,
                    },
                },
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


def search_free_movies(query, genre=None):
    """
    Modern keyless movie search combining IMDb (Hollywood, world cinema, blockbusters)
    and AniList (anime feature films). Supports both text queries and genre filtering.
    """
    results = []
    seen_ids = set()
    genre_clean = genre.strip() if genre and genre.strip().lower() != "all" else None

    # 1. IMDb Modern Suggestion Search (when query is given)
    if query and query.strip():
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
                        if not qid.startswith("tt") or qid in seen_ids:
                            continue
                        seen_ids.add(qid)

                        title = item.get("l") or ""
                        year = item.get("y")
                        qtype = item.get("q") or "movie"
                        stars = item.get("s") or ""
                        img = item.get("i", {}).get("imageUrl") or ""

                        release_date = date(year, 1, 1) if year else None
                        desc = f"Starring: {stars} • Released: {year}" if stars and year else (f"Released: {year}" if year else "Feature Film")

                        movie_genres = ["Movie", qtype.replace("_", " ").title()]
                        if genre_clean and not any(genre_clean.lower() in g.lower() for g in movie_genres):
                            movie_genres.append(genre_clean)

                        results.append({
                            "external_id": f"imdb_{qid}",
                            "media_type": "movie",
                            "media_title": title,
                            "media_description": desc,
                            "media_image": img,
                            "media_release_date": release_date,
                            "media_rate": None,
                            "genre": movie_genres,
                        })
        except Exception:
            pass

    # 2. AniList Anime Movies (handles both query search and genre-based popularity exploration!)
    try:
        gql_query = """
        query ($search: String, $genre: String) {
          Page(page: 1, perPage: 40) {
            media(search: $search, genre: $genre, type: ANIME, format: MOVIE, sort: POPULARITY_DESC) {
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
        search_val = query.strip() if query and query.strip() else None
        resp = requests.post(
            "https://graphql.anilist.co",
            json={"query": gql_query, "variables": {"search": search_val, "genre": genre_clean}},
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


def search_tmdb(query, genre=None):
    """Search TMDB if API key is configured; otherwise fallback to keyless search."""
    api_key = getattr(settings, "TMDB_API_KEY", os.environ.get("TMDB_API_KEY", "")).strip()

    if not api_key:
        return search_free_movies(query, genre=genre)

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
        return results if results else search_free_movies(query, genre=genre)
    except Exception:
        return search_free_movies(query, genre=genre)


def search_open_library(query, genre=None):
    """Search Open Library for novels and books with query and/or genre (subject)."""
    results = []
    genre_clean = genre.strip() if genre and genre.strip().lower() != "all" else None

    # If query is empty but genre is specified, query Open Library subject endpoint
    if (not query or not query.strip()) and genre_clean:
        try:
            subj = genre_clean.lower().replace(" ", "_")
            resp = requests.get(
                f"https://openlibrary.org/subjects/{subj}.json?limit=50",
                headers={"User-Agent": "ReNoteApp/1.0 (contact@renote.local)"},
                timeout=6,
            )
            if resp.status_code == 200:
                works = resp.json().get("works", [])
                for item in works:
                    cover_id = item.get("cover_id")
                    year = item.get("first_publish_year")
                    results.append({
                        "external_id": item.get("key") or "",
                        "media_type": "novel",
                        "media_title": item.get("title") or "",
                        "media_description": "",
                        "media_image": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else "",
                        "media_release_date": _parse_date(str(year)) if year else None,
                        "media_rate": None,
                        "genre": [genre_clean],
                    })
                return results
        except Exception:
            pass

    search_term = (query or "").strip() or (genre_clean or "novel")
    params = {"q": search_term, "limit": 50}
    if genre_clean and query and query.strip():
        params["subject"] = genre_clean

    try:
        resp = requests.get(
            "https://openlibrary.org/search.json",
            params=params,
            headers={"User-Agent": "ReNoteApp/1.0 (contact@renote.local)"},
            timeout=7,
        )
        if resp.status_code == 200:
            data = resp.json().get("docs", [])
            for item in data:
                cover_id = item.get("cover_i")
                year = item.get("first_publish_year")
                subjects = item.get("subject", [])[:5] if item.get("subject") else ([genre_clean] if genre_clean else [])
                results.append({
                    "external_id": item.get("key") or "",
                    "media_type": "novel",
                    "media_title": item.get("title") or "",
                    "media_description": "",
                    "media_image": f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg" if cover_id else "",
                    "media_release_date": _parse_date(str(year)) if year else None,
                    "media_rate": None,
                    "genre": subjects,
                })
    except Exception:
        pass

    return results


def search_local_catalog(query, media_type, genre=None):
    """Fallback search using titles already stored in media_catalog."""
    try:
        from apps.media_catalog.models import Media
        qs = Media.objects.filter(media_type__iexact=media_type)
        if query and query.strip():
            qs = qs.filter(media_title__icontains=query.strip())
        matches = qs[:60]
        results = []
        g_clean = genre.lower().strip() if genre and genre.lower().strip() != "all" else None
        for m in matches:
            genres = m.genre or []
            if g_clean and not any(g_clean in (g or "").lower() for g in genres):
                continue
            results.append({
                "external_id": str(m.external_id),
                "media_type": m.media_type,
                "media_title": m.media_title,
                "media_description": m.media_description,
                "media_image": m.media_image,
                "media_release_date": m.media_release_date,
                "media_rate": float(m.media_rate) if m.media_rate is not None else None,
                "genre": genres,
            })
        return results
    except Exception:
        return []


def search_media(query="", media_type="anime", genre=None):
    """
    Search with in-memory caching and expanded pagination (up to 100 results).
    Supports search by text query, genre filter, or both.
    """
    q = (query or "").strip().lower()
    mtype = (media_type or "anime").strip().lower()
    g = (genre or "").strip()
    if g.lower() == "all":
        g = ""

    if not q and not g:
        return []

    cache_key = f"renote:search:{mtype}:{re.sub(r'\s+', '_', q)}:{re.sub(r'\s+', '_', g.lower())}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    results = []
    try:
        if mtype in ("anime", "manga"):
            try:
                results = search_anilist(q, mtype, genre=g)
            except Exception as e:
                try:
                    results = search_kitsu(q, mtype)
                except Exception:
                    try:
                        results = search_jikan(q, mtype)
                    except Exception:
                        raise e
        elif mtype == "movie":
            results = search_tmdb(q, genre=g)
        elif mtype == "novel":
            results = search_open_library(q, genre=g)

        # Cache valid results for 30 minutes; empty results for 60s
        ttl = 1800 if results else 60
        cache.set(cache_key, results, timeout=ttl)
        return results

    except Exception as e:
        local_results = search_local_catalog(q, mtype, genre=g)
        if local_results:
            cache.set(cache_key, local_results, timeout=300)
            return local_results
        raise e
