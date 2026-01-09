from datetime import datetime
from decimal import Decimal
from typing import Optional
from enum import Enum

from sqlmodel import SQLModel, Field, Column, DECIMAL


class AccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    CASH = "cash"
    BANK = "bank"
    MOBILE_MONEY = "mobile_money"
    INVESTMENT = "investment"
    CREDIT_CARD = "credit_card"


class AccountBase(SQLModel):
    """
    Base model for shared Account fields (used by ORM model and schemas).
    NOTE: When used for the ORM model (in models.py), the Decimal field 
    must be passed with the Column/DECIMAL type hint.
    """
    
    name: str = Field(max_length=255, index=True)
    
    initial_balance: Decimal = Field(
        default=Decimal("0.00"), 
        sa_column=Column(DECIMAL(precision=12, scale=2), nullable=False)
    )

    current_balance: Optional[Decimal] = Field(
        sa_column=Column(DECIMAL(precision=12, scale=2), default=None),
        default=None,
        description="The calculated balance after all transactions. Null if never calculated."
    )
    
    currency: str = Field(default="KES", max_length=5)
    type: AccountType = Field(default=AccountType.CHECKING)
    is_active: bool = Field(default=True)


class AccountCreate(SQLModel):
    """Schema for creating a new account (Input from API)."""
    name: str = Field(max_length=255)
    # Use float for input since JSON uses float
    initial_balance: float = Field(default=0.00) 
    currency: str = Field(default="KES", max_length=5)
    type: AccountType = Field(default=AccountType.CHECKING)
    

class AccountUpdate(SQLModel):
    """Schema for updating an existing account (PATCH Input)."""
    name: str | None = None
    currency: str | None = None
    type: AccountType | None = None
    is_active: bool | None = None


# --- Response Schemas (Output) ---

class AccountRead(SQLModel):
    """Schema for returning account details (GET responses)."""
    id: int
    user_id: int
    
    # Core fields
    name: str
    initial_balance: Decimal
    current_balance: Decimal 
    currency: str
    type: AccountType
    is_active: bool
    
    # Audit fields
    created_by: int | None = None
    updated_by: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    