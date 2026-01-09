from decimal import Decimal
from typing import List, Optional

from sqlmodel import Session, select, func, update

# Import the transaction models and schemas
from app.api.v1.transaction import (
    models as transaction_model,
    schemas as transaction_schema,
)

# --- CRUD Functions (Standard Repository) ---

async def create_transaction(
    session: Session,
    transaction_in: transaction_schema.TransactionCreate,
    user_id: int,
) -> transaction_model.Transaction:
    """
    Creates a new transaction linked to a specific user and account.
    """
    # 1. Prepare data for model instantiation
    transaction_data = transaction_in.model_dump()
    
    # 2. Safely convert the float amount to a high-precision Decimal
    amount_decimal = Decimal(str(transaction_data.pop("amount")))
    
    # 3. Create Transaction instance
    transaction_obj = transaction_model.Transaction.model_validate(
        transaction_in,
        update={
            "user_id": user_id,
            "amount": amount_decimal, 
        },
    )

    # 4. Persist to DB
    session.add(transaction_obj)
    session.commit()
    session.refresh(transaction_obj)
    
    return transaction_obj


async def get_transaction_by_id(
    session: Session, 
    transaction_id: int,
    user_id: int, 
) -> transaction_model.Transaction | None:
    """
    Fetches a specific transaction, enforcing ownership (user_id).
    """
    statement = (
        select(transaction_model.Transaction)
        .where(transaction_model.Transaction.id == transaction_id)
        .where(transaction_model.Transaction.user_id == user_id)
    )
    transaction = session.exec(statement).first()
    
    return transaction


# async def get_user_transactions(
#     session: Session,
#     user_id: int,
#     skip: int = 0,
#     limit: int = 100,
# ) -> List[transaction_model.Transaction]:
#     """
#     Fetches a paginated list of all transactions owned by a specific user.
#     """
#     statement = (
#         select(transaction_model.Transaction)
#         .where(transaction_model.Transaction.user_id == user_id)
#         .order_by(transaction_model.Transaction.transaction_date.desc())
#         .offset(skip)
#         .limit(limit)
#     )
#     transactions = session.exec(statement).all()
    
#     return list(transactions)


async def get_user_transactions(
    session: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[transaction_model.Transaction]:
    """
    Fetches a paginated list of all transactions owned by a specific user.
    """
    statement = (
        select(transaction_model.Transaction)
        .where(transaction_model.Transaction.user_id == user_id)
        .order_by(transaction_model.Transaction.transaction_date.desc())
        .offset(skip)
        .limit(limit)
    )
    
    transactions = session.exec(statement).all()
    
    return transactions


async def update_transaction(
    session: Session,
    db_transaction: transaction_model.Transaction,
    transaction_update: transaction_schema.TransactionUpdateReq,
) -> transaction_model.Transaction:
    """
    Updates the transaction record with non-financial details 
    (e.g., description, category_id, notes).
    """
    # 1. Get update data, excluding fields that weren't set (for PATCH request)
    update_data = transaction_update.model_dump(exclude_unset=True)
    
    # 1. Iterate over the update fields
    for key, value in update_data.items():
        # 2. Assign the new value to the existing ORM object
        setattr(db_transaction, key, value)
    
    # 3. Persist the changes
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    
    return db_transaction


async def delete_transaction(
    session: Session,
    db_transaction: transaction_model.Transaction,
) -> None:
    """
    Deletes a transaction from the database.
    """
    session.delete(db_transaction)
    session.commit()
    

async def get_account_total_flow(
    session: Session,
    account_id: int,
    flow_type: transaction_schema.TransactionType, # INCOME or EXPENSE
) -> Decimal:
    """
    Calculates the total income or total expense for a specific account.
    """
    statement = select(
        func.coalesce(func.sum(transaction_model.Transaction.amount), Decimal('0.00'))
    ).where(
        transaction_model.Transaction.account_id == account_id,
        transaction_model.Transaction.transaction_type == flow_type,
    )
    
    total = session.exec(statement).one()
    
    return total
