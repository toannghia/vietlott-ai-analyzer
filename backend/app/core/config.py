from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Vietlott Analyzer"
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me"

    DATABASE_URL: str = "postgresql+asyncpg://vietlott:vietlott_secret_2024@localhost:5435/vietlott_db"
    DATABASE_URL_SYNC: str = "postgresql+psycopg://vietlott:vietlott_secret_2024@localhost:5435/vietlott_db"
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env.local", env_ignore_empty=True, extra="ignore"
    )
    
    # Telegram Fallback
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""


@lru_cache()
def get_settings() -> Settings:
    return Settings()
