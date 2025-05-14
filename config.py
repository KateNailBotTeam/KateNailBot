import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False
    )
    BOT_TOKEN: str = os.getenv("BOT_TOKEN")


settings = Settings()