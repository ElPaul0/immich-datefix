from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    immich_url: str = "http://immich-server:2283"
    immich_api_key: str = ""
    data_dir: Path = Path("/data")
    # Date-only filenames (WhatsApp…) → heure locale utilisée
    default_hour: int = 12
    default_minute: int = 0
    # Écart minimal (secondes) pour proposer une correction
    min_delta_seconds: int = 12 * 3600
    page_size: int = 500
    host: str = "0.0.0.0"
    port: int = 8080


def get_settings() -> Settings:
    return Settings()
