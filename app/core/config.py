from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

# Project root directory (mindmate_proj/)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # LLM Provider: "groq" (default, free) or "openai"
    LLM_PROVIDER: str = "groq"

    # Groq (free, fast, open-source models)
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # OpenAI (optional fallback)
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4.1-nano"

    # Embeddings (local, free) — BGE-small has better accuracy than MiniLM at similar speed
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    # Database — defaults to local SQLite
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR / 'app' / 'data' / 'mindmate.db'}"

    # ChromaDB vector store path
    CHROMA_PATH: str = str(BASE_DIR / "app" / "data" / "chroma")

    # CORS origins for frontend
    CORS_ORIGINS: str = "http://localhost:3000"

    # Auth
    REQUIRE_AUTH: bool = False

    # Langfuse (optional)
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: str = ""
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # Email (optional)
    EMAIL_HOST: str = ""
    EMAIL_PORT: int = 587
    EMAIL_USER: str = ""
    EMAIL_PASS: str = ""

    @property
    def langfuse_enabled(self) -> bool:
        return bool(self.LANGFUSE_PUBLIC_KEY and self.LANGFUSE_SECRET_KEY)

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
