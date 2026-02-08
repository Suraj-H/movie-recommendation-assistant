"""Convert dataset rows to Haystack Documents. Single place for schema mapping."""
from haystack.dataclasses import Document

# Sanity cap for content/title to avoid huge payloads
MAX_CONTENT_LENGTH = 50_000
MAX_TITLE_LENGTH = 500


def _safe_float(value, default: float = 5.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_genre_list(genre_raw) -> list[str]:
    """Return lowercase genre list; spaces in each genre become underscores (Qdrant keyword index)."""
    if isinstance(genre_raw, str):
        return [g.strip().lower().replace(" ", "_") for g in genre_raw.split(",") if g.strip()]
    return []


def _sanitize_str(value: str, max_len: int) -> str:
    if not isinstance(value, str):
        return ""
    s = value.strip()
    return s[:max_len] if len(s) > max_len else s


def movie_to_document(movie_dataset) -> list[Document]:
    """Convert iterable of movie rows to list of Haystack Documents."""
    docs = []
    for movie in movie_dataset:
        rating = _safe_float(movie.get("Vote_Average"), 5.0)
        genre_list = _safe_genre_list(movie.get("Genre"))
        content = _sanitize_str(movie.get("Overview", "") or "", MAX_CONTENT_LENGTH)
        title = _sanitize_str(movie.get("Title", "") or "", MAX_TITLE_LENGTH)
        language = _sanitize_str(movie.get("Original_Language", "") or "", 10).lower()

        doc = Document(
            content=content,
            meta={
                "title": title,
                "rating": rating,
                "genre": genre_list,
                "language": language,
            },
        )
        docs.append(doc)
    return docs
