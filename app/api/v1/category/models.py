# app/api/v1/category/models.py (Proposed Final Fix)

from typing import List, Optional
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel # Ensure these are imported
from app.api.v1.category.schemas import CategoryBase # Assuming you have a CategoryBase


class Category(CategoryBase, table=True):
    """
    Database model for transaction categories.
    """
    __tablename__ = "category"

    id: Optional[int] = Field(default=None, primary_key=True)
    
    user_id: int = Field(index=True, foreign_key="user.id")

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

    user: "User" = Relationship(
        back_populates="categories",
        sa_relationship_kwargs={"foreign_keys": "[Category.user_id]"}
    )
    
    # Back-link to Transactions (assuming the foreign key is correctly defined on the Transaction model)
    transactions: List["Transaction"] = Relationship(back_populates="category")
    