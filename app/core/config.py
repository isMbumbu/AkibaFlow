from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Project Settings
    PROJECT_NAME: str = "AkibaFlow - Budgeting App"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings
    DATABASE_URL: str
    
    # Security/Auth Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Environment
    ENVIRONMENT: str = "development" # development | production
    
    class Config:
        env_file = ".env"

settings = Settings()
