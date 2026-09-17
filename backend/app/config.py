from pydantic_settings import BaseSettings
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "IA EXPRESS - Motor 1: Indexación Exprés"
    DEBUG: bool = True
    PORT: int = 8050
    BASE_URL: str = os.getenv("BASE_URL", "http://194.164.161.104")
    
    # IndexNow Protocol Configuration
    INDEXNOW_KEY: str = "iaexpress2026indexkey883921"
    
    @property
    def INDEXNOW_KEY_LOCATION(self) -> str:
        return f"{self.BASE_URL.rstrip('/')}/{self.INDEXNOW_KEY}.txt"

    INDEXNOW_ENDPOINTS: list[str] = [
        "https://api.indexnow.org/IndexNow",
        "https://www.bing.com/IndexNow"
    ]

    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/ia_express.db"
    PUBLIC_DIR: Path = BASE_DIR / "public"

settings = Settings()
