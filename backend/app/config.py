from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    APP_NAME: str = "Ride Tracker API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    PRODUCTION: bool = False

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 7

    ALLOWED_ORIGINS: str = "http://localhost:4321"

    @property
    def origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = str(_ENV_FILE)
        case_sensitive = True


settings = Settings()
