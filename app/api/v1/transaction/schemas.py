from enum import Enum
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import SQLModel, Field, Column, DECIMAL # Keep DECIMAL for field configuration


class TransactionType(str, Enum):
    """Defines the direction of the money flow."""
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TRANSFER = "TRANSFER"


class TransactionBase(SQLModel):
    """Base fields for Transaction, including Decimal setup for ORM."""
    
    # Financial Core
    amount: Decimal = Field(
        sa_column=Column(DECIMAL(precision=12, scale=2), nullable=False),
        description="The monetary value of the transaction."
    )
    transaction_type: TransactionType = Field(description="INCOME or EXPENSE.")
    
    # Relationships (Foreign Keys)
    account_id: int = Field(
        index=True, 
        foreign_key="account.id",  # <--- CRITICAL FIX APPLIED
        description="The account where this transaction occurred."
    )
    category_id: int = Field(
        index=True, 
        foreign_key="category.id", # <--- CRITICAL FIX APPLIED
        description="The category for reporting."
    )
    # Metadata
    description: str = Field(max_length=512)
    transaction_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Future SMS Ambition Fields
    is_automated: bool = Field(default=False)
    raw_text: Optional[str] = Field(default=None)


class TransactionCreate(SQLModel):
    """Input for manually creating a transaction (Input from API)."""
    
    amount: float
    transaction_type: TransactionType
    account_id: int
    category_id: int
    description: str | None = None
    transaction_date: datetime = Field(default_factory=datetime.utcnow)


class TransactionRead(TransactionBase):
    """Output for displaying transaction details."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None
    