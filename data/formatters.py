"""Format document lists for tool output (LLM-facing string)."""
from haystack.dataclasses import Document


def movie_to_string(documents: list[Document]) -> str:
    """Format retrieved movie documents as a single string for the agent tool output."""
    parts = []
    for doc in documents:
        title = doc.meta.get("title", "No Title")
        content = doc.content or ""
        rating = doc.meta.get("rating", "N/A")
        genre = doc.meta.get("genre", [])
        genre_display = [g.replace("_", " ") for g in genre] if isinstance(genre, list) else genre
        parts.append(
            f"Movie details for {title}:\n{content}\nRating:{rating}\nGenres:{genre_display}\n\n"
        )
    return "".join(parts)
