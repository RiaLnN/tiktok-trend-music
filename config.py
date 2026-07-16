"""
Конфигурация приложения.

Все значения читаются из переменных окружения / файла .env
(см. .env.example). Держим конфиг в одном месте, чтобы остальной
код не знал про os.environ вообще.
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    # --- Telegram ---
    BOT_TOKEN: str = ""

    # --- RapidAPI: tiktok-scraper7 ---
    RAPIDAPI_KEY: str = ""
    RAPIDAPI_HOST: str = "tiktok-scraper7.p.rapidapi.com"

    # --- Доступ ---
    # Telegram user_id владельца(-ев) бота через запятую, например "123456789,987654321".
    # Эти пользователи получают доступ к /grant, /revoke, /subinfo, /admin.
    ADMIN_IDS: str = ""

    # --- Пути для хранения данных бота ---
    DATA_DIR: Path = BASE_DIR / "data"
    AUDIO_DIR: Path = BASE_DIR / "data" / "audio"
    SETTINGS_FILE: Path = BASE_DIR / "data" / "user_settings.json"
    SUBSCRIPTIONS_FILE: Path = BASE_DIR / "data" / "subscriptions.json"

    # --- Сеть ---
    HTTP_TIMEOUT: float = 30.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def admin_id_list(self) -> list[int]:
        """ADMIN_IDS как список int. Хранится строкой, чтобы не зависеть от
        особенностей парсинга списков переменных окружения в pydantic-settings."""
        return [int(chunk.strip()) for chunk in self.ADMIN_IDS.split(",") if chunk.strip()]


settings = Settings()

# Гарантируем, что папки для аудио/настроек существуют ещё до старта бота.
settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)