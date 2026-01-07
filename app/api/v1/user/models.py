from zoneinfo import ZoneInfo
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel, Relationship
from typing import List

from app.core.config import settings
from app.api.v1.user import schemas as user_schemas
from app.api.v1.account import models as account_models 
from app.api.v1.transaction import models as transaction_models
from app.api.v1.category import models as category_models


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
    accounts: List["Account"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[Account.user_id]"} 
    )

    transactions: List["Transaction"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[Transaction.user_id]"} 
    )
    
    # One User has many Categories
    categories: List["Category"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[Category.user_id]"}
    )