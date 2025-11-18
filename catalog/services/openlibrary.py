# catalog/services/openlibrary.py
import requests

BASE_URL = "https://openlibrary.org"


def search_books(query, limit=5):
    if not query:
        return []

    params = {
        "q": query,
        "limit": limit,
    }

    try:
        resp = requests.get(f"{BASE_URL}/search.json", params=params, timeout=5)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    data = resp.json()
    results = []

    for raw in data.get("docs", [])[:limit]:
        title = raw.get("title") or ""
        author_names = raw.get("author_name") or []
        year = raw.get("first_publish_year")
        key = raw.get("key")  # e.g. "/works/OL12345W"

        if not key:
            continue

        url = f"{BASE_URL}{key}"

        cover_id = raw.get("cover_i")
        thumbnail_url = (
            f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
            if cover_id
            else ""
        )

        subtitle_parts = []
        if author_names:
            subtitle_parts.append(", ".join(author_names[:2]))
        if year:
            subtitle_parts.append(str(year))

        subtitle = " · ".join(subtitle_parts)

        results.append(
            {
                "source": "openlibrary",
                "external_id": key,
                "title": title,
                "item_type": "book",
                "url": url,
                "thumbnail_url": thumbnail_url,
                "meta": {
                    "authors": author_names,
                    "year": year,
                    "subtitle": subtitle,
                },
            }
        )
    return results
