from pydantic_settings import BaseSettings
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "IA EXPRESS - Motor 1: Indexación Exprés"
    DEBUG: bool = True
    PORT: int = 8050
    BASE_URL: str = "http://localhost:8050"
    
    # IndexNow Protocol Configuration
    INDEXNOW_KEY: str = "iaexpress2026indexkey883921"
    INDEXNOW_KEY_LOCATION: str = "http://localhost:8050/iaexpress2026indexkey883921.txt"
    INDEXNOW_ENDPOINTS: list[str] = [
        "https://api.indexnow.org/IndexNow",
        "https://www.bing.com/IndexNow"
    ]

    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/ia_express.db"
    PUBLIC_DIR: Path = BASE_DIR / "public"

settings = Settings()
