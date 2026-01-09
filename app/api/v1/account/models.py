from datetime import datetime, timezone 
from decimal import Decimal
from typing import List

from sqlmodel import Field, SQLModel, Relationship 
from app.api.v1.account.schemas import AccountBase


class Account(AccountBase, table=True):
    """Database model for a user's financial account."""
    
    id: int | None = Field(default=None, primary_key=True)
    
    user_id: int = Field(index=True, foreign_key="user.id")

    created_by: int | None = Field(foreign_key='user.id', default=None)
    updated_by: int | None = Field(foreign_key='user.id', default=None)
    
    created_at: datetime | None = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        nullable=False
    )
    
    updated_at: datetime | None = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
        sa_column_kwargs={
            'onupdate': lambda: datetime.now(tz=timezone.utc)
        }
    )
    
    # Relationships would go here
    user: "User" = Relationship(
        back_populates="accounts",
        sa_relationship_kwargs={
            "foreign_keys": "[Account.user_id]" 
        }
    )
    
    # Link to Transactions (Needs string literal)
    transactions: List["Transaction"] = Relationship(back_populates="account")