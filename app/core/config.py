import secrets

from typing import Literal, Any, Annotated

from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import (
    PostgresDsn, EmailStr, BeforeValidator, AnyUrl, computed_field)


def parse_cors(v: Any) -> list[str] | str:
    """Parse CORS origins from a string or list."""
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """Application settings configuration."""

    model_config = SettingsConfigDict(
        # Use top level .env file
        env_file='../../.env',
        env_ignore_empty=True,
        extra='ignore',
    )

    APP_TIMEZONE: str = 'Africa/Nairobi'

    # Basic app configuration
    PROJECT_NAME: str = 'SokoPay API'
    API_VERSION_STR: str = '/api/v1'
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 2 days = 2 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 2
    ENVIRONMENT: Literal['local', 'staging', 'production'] = 'local'

    BACKEND_HOST: str = 'http://localhost:8000'
    FRONTEND_HOST: str = 'http://localhost:5173'
    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip('/') for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    # Database configuration
    POSTGRES_SERVER: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: int = 5432

    # Redis configuration
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # AT Configs
    AT_API_KEY: str
    AT_API_USERNAME: str

    TESTING: bool = False

    # Removed: MPESA Configs (MPESA_FS_SERVICE_NUMBER, etc.)
    # Removed: TNCS_URL

    OTP_EXPIRE_MINUTES: int = 30
    SEND_NOTIFICATIONS: bool = False

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        if self.TESTING:
            self.POSTGRES_DB = f'{self.POSTGRES_DB}-test'
            self.POSTGRES_SERVER = f'{self.POSTGRES_SERVER}-test'

        return MultiHostUrl.build(
            scheme='postgresql+psycopg',
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    FIRST_SUPERUSER_PHONE: str | None = None
    FIRST_SUPERUSER_OTP: str | None = None


settings = Settings()