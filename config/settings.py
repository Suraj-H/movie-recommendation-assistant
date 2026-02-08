"""Load and expose env-based settings. Validates only when needed (index/query)."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    qdrant_index_name: str
    hf_token: str

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            openai_api_key=os.environ.get("OPENAI_API_KEY", "").strip(),
            qdrant_url=os.environ.get("QDRANT_URL", "").strip(),
            qdrant_api_key=os.environ.get("QDRANT_API_KEY", "").strip(),
            qdrant_index_name=os.environ.get("QDRANT_INDEX_NAME", "movie-assistant").strip()
            or "movie-assistant",
            hf_token=os.environ.get("HF_TOKEN", "").strip(),
        )

    def require_openai(self) -> None:
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not set. Set it in .env or environment.")

    def require_qdrant(self) -> None:
        if not self.qdrant_url or not self.qdrant_api_key:
            raise ValueError(
                "QDRANT_URL and QDRANT_API_KEY must be set. Set them in .env or environment."
            )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings.from_env()
    return _settings
