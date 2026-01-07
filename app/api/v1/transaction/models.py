from typing import Optional

from sqlmodel import Field, Relationship # Ensure Relationship is imported

# Assuming TimeStampedModel definition is accessible via imports or implicitly handled
# We use TransactionBase from the same module structure
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
    
    account: "Account" = Relationship(back_populates="transactions") 

    category: "Category" = Relationship(back_populates="transactions")