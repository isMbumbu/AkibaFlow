from decimal import Decimal
from sqlmodel import Session, select, update

from app.api.v1.account import (
    models as account_model, 
    schemas as account_schema
)

# --- CRUD Functions (Standard Repository) ---

async def create_account(
    session: Session,
    account_in: account_schema.AccountCreate,
    user_id: int,
) -> account_model.Account:
    """
    Creates a new account linked to a specific user.
    Note: Converts initial_balance (float from API) to Decimal for storage.
    """
    # 1. Create Account instance
    # Note: current_balance will be None initially, which is handled in update_account_balance
    account_obj = account_model.Account.model_validate(
        account_in,
        update={
            "user_id": user_id,
            "initial_balance": Decimal(str(account_in.initial_balance)) # Safe conversion
        },
    )

    # 2. Persist to DB
    session.add(account_obj)
    session.commit()
    session.refresh(account_obj)
    
    return account_obj


async def get_user_accounts(
    session: Session,
    user_id: int,
) -> list[account_model.Account]:
    """
    Fetches all active accounts owned by a specific user.
    """
    statement = (
        select(account_model.Account)
        .where(account_model.Account.user_id == user_id)
        .where(account_model.Account.is_active == True)
        .order_by(account_model.Account.created_at)
    )
    accounts = session.exec(statement).all()
    
    return list(accounts)


async def get_account_by_id(
    session: Session, 
    account_id: int,
    user_id: int, 
) -> account_model.Account | None:
    """
    Fetches a specific account, enforcing ownership (user_id).
    """
    statement = (
        select(account_model.Account)
        .where(account_model.Account.id == account_id)
        .where(account_model.Account.user_id == user_id)
    )
    account = session.exec(statement).first()
    
    return account


async def update_account(
    session: Session,
    db_account: account_model.Account,
    account_update: account_schema.AccountUpdate,
) -> account_model.Account:
    """
    Applies updates to an existing account model.
    """
    # 1. Merge the data from the Pydantic schema into the SQLModel instance
    update_data = account_update.model_dump(exclude_unset=True)
    
    # 2. Iterate and update
    for key, value in update_data.items():
        setattr(db_account, key, value)
    
    # 3. Persist changes
    session.add(db_account)
    session.commit()
    session.refresh(db_account)
    
    return db_account


# --- Helper/Business Logic Functions ---

# REMOVED: calculate_current_balance (It was a redundant placeholder, logic is in service/routes)


async def get_account_details(
    session: Session,
    account_id: int,
    user_id: int,
) -> account_model.Account | None:
    """
    Retrieves account details by ID, enforcing ownership.
    """
    # Simply retrieves the account; the balance conversion is done in the routes layer.
    account = await get_account_by_id(
        session=session,
        account_id=account_id,
        user_id=user_id,
    )
    
    return account


async def delete_account(
    session: Session,
    account_id: int,
    user_id: int,
) -> None:
    """
    Soft-deletes (deactivates) an account by setting is_active to False.
    """
    statement = (
        update(account_model.Account)
        .where(account_model.Account.id == account_id)
        .where(account_model.Account.user_id == user_id)
        .values(is_active=False)
    )
    session.exec(statement)
    session.commit()


async def update_account_balance(
    session: Session,
    account: account_model.Account,
    balance_change: Decimal,
) -> account_model.Account:
    """
    Applies a calculated change to the account's current_balance and persists it.
    
    The transaction service calculates the 'balance_change' (positive or negative)
    and passes it here to update the account record.
    """
    
    # 1. Get the current balance value (if none exists, use initial balance)
    current_balance = account.current_balance if account.current_balance is not None else account.initial_balance
    
    # 2. Apply the change
    new_balance = current_balance + balance_change
    
    # 3. Update the ORM object
    account.current_balance = new_balance
    
    # 4. Persist the changes
    session.add(account)
    session.commit()
    session.refresh(account)
    
    return account
