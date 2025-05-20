import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False
    )
    BOT_TOKEN: Optional[str] = os.getenv("BOT_TOKEN")
    admin_ids: frozenset[int] = frozenset((468880541,))


settings = Settings()
