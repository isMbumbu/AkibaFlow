from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # Project Settings
    PROJECT_NAME: str = "AkibaFlow - Budgeting App"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: Optional[str] = None
    
    # Security/Auth Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Celery/Redis (Optional - for later implementation)
    REDIS_HOST: Optional[str] = None
    REDIS_PORT: Optional[int] = None
    CELERY_BROKER_URL: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@db:5432/{self.POSTGRES_DB}"

settings = Settings()
