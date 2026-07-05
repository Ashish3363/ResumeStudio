# App settings via pydantic-settings; loads env (DATABASE_URL, JWT_SECRET, GEMINI_API_KEY, storage creds).

from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore", #ignore unrelated env vars instead of erroring
    )

    # --- app ---
    APP_ENV: str = "dev"          # dev | prod
    DEBUG: bool = True

    # --- database (Neon / local Postgres) ---
    DATABASE_URL: str             # e.g. postgresql+psycopg://user:pass@host/dbname

    # --- auth / jwt ---
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TTL_MIN: int = 15
    JWT_REFRESH_TTL_DAYS: int = 30

    # --- ai ---
    GEMINI_API_KEY: str

    # --- storage (S3-compatible: R2 / Supabase) ---
    STORAGE_ENDPOINT: str = ""
    STORAGE_BUCKET: str = ""
    STORAGE_ACCESS_KEY: str = ""
    STORAGE_SECRET_KEY: str = ""

    # --- product rules ---
    SAVED_RESUME_CAP: int = 10    # the FIFO cap; single source of truth for the "10" limit

    # --- cors ---
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v):
        # allow CORS_ORIGINS in .env as a comma-separated string
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
