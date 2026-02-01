from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "SentientVoice"
    API_V1_STR: str = "/api/v1"
    
    # Security
    HIPAA_MODE: bool = True
    SECRET_KEY: str = "changelethis"
    ENCRYPTION_KEY: str
    DATABASE_URL: str
    
    # API Keys (Critical)
    DEEPGRAM_API_KEY: str
    GROQ_API_KEY: str
    ELEVENLABS_API_KEY: str
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
