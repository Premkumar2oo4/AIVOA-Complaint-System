from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://aivoa:aivoa_password@localhost:5432/aivoa_complaints"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    frontend_url: str = "http://localhost:5173"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()

