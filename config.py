"""Application configuration.

All values are read from environment variables/.env file
(see .env.example). We keep the config in one place so that the rest
The code didn't know about os.environ at all."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    # --- Telegram ---
    BOT_TOKEN: str = ""

    # --- RapidAPI: tiktok-scraper7 ---
    RAPIDAPI_KEY: str = ""
    RAPIDAPI_HOST: str = "tiktok-scraper7.p.rapidapi.com"

    # --- Access ---
    # Telegram user_id of the bot owner(s), separated by commas, for example "123456789,987654321".
    # These users have access to /grant, /revoke, /subinfo, /admin.
    ADMIN_IDS: str = ""

    # --- Paths for storing bot data ---
    DATA_DIR: Path = BASE_DIR / "data"
    AUDIO_DIR: Path = BASE_DIR / "data" / "audio"
    SETTINGS_FILE: Path = BASE_DIR / "data" / "user_settings.json"
    SUBSCRIPTIONS_FILE: Path = BASE_DIR / "data" / "subscriptions.json"

    # --- Net ---
    HTTP_TIMEOUT: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def admin_id_list(self) -> list[int]:
        """ADMIN_IDS as a list of ints. Stored as a string so as not to depend on
        features of parsing lists of environment variables in pydantic-settings."""
        return [int(chunk.strip()) for chunk in self.ADMIN_IDS.split(",") if chunk.strip()]


settings = Settings()

# We guarantee that folders for audio/settings exist even before the bot starts.
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)