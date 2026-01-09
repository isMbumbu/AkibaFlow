from typing import Optional

from sqlmodel import Field, Relationship
from datetime import datetime, timezone

from app.api.v1.transaction.schemas import TransactionBase


class Transaction(TransactionBase, table=True):
    """
    The main financial record model.
    """
    __tablename__ = "transaction"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: int = Field(index=True, foreign_key="user.id")

    
    user: "User" = Relationship(
        back_populates="transactions",
        sa_relationship_kwargs={"foreign_keys": "[Transaction.user_id]"}
    )

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

    
    account: "Account" = Relationship(back_populates="transactions") 

    category: "Category" = Relationship(back_populates="transactions")
