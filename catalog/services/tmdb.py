# catalog/services/tmdb.py
import requests
from django.conf import settings

BASE_URL = "https://api.themoviedb.org/3"


def search_movies(query, limit=5):
    """
    Search TMDB for movies/TV by title.
    Returns a list of normalized dicts.
    """
    api_key = settings.TMDB_API_KEY
    if not api_key or not query:
        return []

    params = {
        "api_key": api_key,
        "query": query,
        "include_adult": False,
    }

    try:
        resp = requests.get(f"{BASE_URL}/search/multi", params=params, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    data = resp.json()
    results = []
    for raw in data.get("results", [])[:limit]:
        media_type = raw.get("media_type")
        if media_type not in ("movie", "tv"):
            continue

        title = raw.get("title") or raw.get("name") or ""
        year = None
        date_str = raw.get("release_date") or raw.get("first_air_date")
        if date_str:
            year = date_str.split("-")[0]

        poster_path = raw.get("poster_path")
        thumbnail_url = (
            f"https://image.tmdb.org/t/p/w185{poster_path}" if poster_path else ""
        )

        external_id = f"{media_type}:{raw.get('id')}"

        url = f"https://www.themoviedb.org/{media_type}/{raw.get('id')}"

        subtitle_parts = []
        if year:
            subtitle_parts.append(str(year))
        if media_type == "movie":
            subtitle_parts.append("Movie")
        elif media_type == "tv":
            subtitle_parts.append("TV")

        subtitle = " · ".join(subtitle_parts)

        results.append(
            {
                "source": "tmdb",
                "external_id": external_id,
                "title": title,
                "item_type": "movie",  # fits our ItemType.MOVIE bucket
                "url": url,
                "thumbnail_url": thumbnail_url,
                "meta": {
                    "year": year,
                    "subtitle": subtitle,
                    "overview": raw.get("overview") or "",
                },
            }
        )
    return results
