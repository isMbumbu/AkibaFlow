from enum import Enum
from sqlmodel import SQLModel, Field
from typing import Optional


class DefaultCategoryName(str, Enum):
    """
    Standard, system-provided category names for initial user setup.
    """
    SALARY = "Salary"
    FOOD = "Food"
    RENT = "Rent/Housing"
    TRANSPORT = "Transport"
    UTILITIES = "Utilities"
    ENTERTAINMENT = "Entertainment"
    MISCELLANEOUS = "Miscellaneous"


class CategoryBase(SQLModel):
    """
    Defines the core properties of a Category.
    """
    
    name: str = Field(max_length=100, index=True)
    
    system_name: Optional[DefaultCategoryName] = Field(
        default=None,
        description="Maps custom categories back to a standard set for better analytics."
    )
    
    is_custom: bool = Field(default=True)
    
    user_id: Optional[int] = Field(default=None, index=True)


class CategoryCreate(SQLModel):
    """Input schema for creating a new category."""
    name: str
    system_name: Optional[DefaultCategoryName] = Field(default=None)


class CategoryRead(CategoryBase):
    """Output schema for reading category details."""
    id: int