from zoneinfo import ZoneInfo
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.core.config import settings
from app.api.v1.user import schemas as user_schemas


class User(user_schemas.UserBase, table=True):
    """
    Database model for user, table inferred from class name
    """

    id: int | None = Field(default=None, primary_key=True)
    is_superuser: bool = False
    hashed_password: str
    created_by: int | None = Field(foreign_key='user.id', default=None)
    updated_by: int | None = Field(foreign_key='user.id', default=None)
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        sa_column_kwargs={
            'onupdate': lambda: datetime.now(tz=timezone.utc)
        }
    )