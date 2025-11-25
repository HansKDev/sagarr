import os
from pydantic_settings import BaseSettings
import uuid

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sagarr"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key_change_me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week

    # Plex Config
    PLEX_PRODUCT: str = "Sagarr"
    PLEX_CLIENT_ID: str = os.getenv("PLEX_CLIENT_ID", str(uuid.uuid4()))
    PLEX_DEVICE: str = "Sagarr Server"
    PLEX_VERSION: str = "0.1.0"
    
    # URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # Tautulli
    TAUTULLI_URL: str = os.getenv("TAUTULLI_URL", "")
    TAUTULLI_API_KEY: str = os.getenv("TAUTULLI_API_KEY", "")

    # Overseerr
    OVERSEERR_URL: str = os.getenv("OVERSEERR_URL", "")
    OVERSEERR_API_KEY: str = os.getenv("OVERSEERR_API_KEY", "")

    # AI
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "openai") # openai, generic
    AI_API_KEY: str = os.getenv("AI_API_KEY", "")
    AI_BASE_URL: str = os.getenv("AI_BASE_URL", "") # For generic/ollama
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-3.5-turbo")

    class Config:
        env_file = ".env"

settings = Settings()
