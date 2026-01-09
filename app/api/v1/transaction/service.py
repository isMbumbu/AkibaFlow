from decimal import Decimal
from typing import List, Optional

from fastapi import status, HTTPException
from sqlmodel import Session

from app.core.logging_config import app_logger

from app.api.v1.transaction import (
    repository as transaction_repo,
    schemas as transaction_schema,
    models as transaction_model,
)
from app.api.v1.account import (
    models as account_model,
    repository as account_repo, # <-- Account Repository for balance updates
)
from app.api.v1.transaction.schemas import TransactionType


# --- Internal Helper Function (Business Logic) ---

def _calculate_balance_change(
    transaction: transaction_model.Transaction,
    reverse: bool = False
) -> Decimal:
    """
    Calculates the impact of a transaction on its account balance.
    Raises HTTPException 400 if it's an unsupported type (TRANSFER).
    """
    amount = transaction.amount # Already a Decimal

    if transaction.transaction_type == TransactionType.TRANSFER:
        # Prevents unintended balance changes for transfers
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TRANSFER transactions cannot be processed by this single-account flow."
        )

    if transaction.transaction_type == TransactionType.INCOME:
        change = amount
    else: # EXPENSE
        change = -amount

    return -change if reverse else change


# --- CRUD and Business Logic Functions ---

async def create_new_transaction(
    session: Session,
    transaction_in: transaction_schema.TransactionCreate,
    user_id: int,
) -> transaction_model.Transaction:
    """
    Creates the transaction and updates the corresponding account balance via Account Repository.
    """
    try:
        app_logger.info(
            msg=f'Request to create new transaction for user {user_id}'
        )

        # 1. Get the target account (Checks ownership)
        account_to_update = await account_repo.get_account_by_id(
            session=session,
            account_id=transaction_in.account_id,
            user_id=user_id
        )

        if not account_to_update:
            app_logger.warning(
                msg=f'Account {transaction_in.account_id} not found or access denied for user {user_id}'
            )
            raise HTTPException(
                detail="Account not found or access denied.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # 2. Calculate balance change (checks for TRANSFER)
        temp_transaction = transaction_model.Transaction(
            transaction_type=transaction_in.transaction_type,
            amount=Decimal(str(transaction_in.amount))
        )
        balance_change = _calculate_balance_change(temp_transaction)

        # 3. Create the transaction record
        new_transaction = await transaction_repo.create_transaction(
            session=session,
            transaction_in=transaction_in,
            user_id=user_id,
        )

        # 4. Update account balance (DELEGATED TO ACCOUNT REPOSITORY)
        await account_repo.update_account_balance(
            session=session,
            account=account_to_update,
            balance_change=balance_change
        )
        
        session.refresh(new_transaction)

        app_logger.info(
            msg=f'Transaction {new_transaction.id} created successfully for user {user_id}'
        )

        return new_transaction

    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        app_logger.error(
            msg=f'Server Error creating transaction for user {user_id}: {e}'
        )
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_single_transaction(
    session: Session,
    transaction_id: int,
    user_id: int,
) -> transaction_model.Transaction:
    """
    Retrieves a single transaction by ID, enforcing user ownership.
    """
    try:
        app_logger.info(
            msg=f'Request to fetch transaction {transaction_id} for user {user_id}'
        )
        transaction = await transaction_repo.get_transaction_by_id(
            session=session,
            transaction_id=transaction_id,
            user_id=user_id,
        )

        if not transaction:
            app_logger.warning(
                msg=f'Transaction {transaction_id} not found or access denied for user {user_id}'
            )
            raise HTTPException(
                detail="Transaction not found or access denied.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return transaction

    except HTTPException as e:
        raise e
    except Exception as e:
        app_logger.error(
            msg=f'Server Error fetching transaction {transaction_id}: {e}'
        )
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_list_transactions(
    session: Session, # This is typically a synchronous Session in FastAPI
    user_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[transaction_model.Transaction]:
    """
    Retrieves a paginated list of all transactions for the user.
    """
    try:
        app_logger.info(
            msg=f'Request to list transactions for user {user_id} (skip={skip}, limit={limit})'
        )
        # 1. Fetch transactions via repository
        transactions = await transaction_repo.get_user_transactions(
            session=session,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
        
        # 2. CRITICAL FIX: Ensure all objects have their server-generated fields loaded.
        # This must be done on the synchronous session object.
        for tx in transactions:
            session.refresh(tx) # Synchronous refresh on the synchronous session
        
        return transactions

    except Exception as e:
        app_logger.error(
            msg=f'Server Error listing transactions for user {user_id}: {e}'
        )
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    

async def update_transaction(
    session: Session,
    transaction_id: int,
    transaction_update: transaction_schema.TransactionUpdateReq,
    user_id: int,
) -> transaction_model.Transaction:
    """
    Updates non-financial fields of a transaction.
    """
    try:
        app_logger.info(
            msg=f'Request to update transaction {transaction_id} for user {user_id}'
        )

        # 1. Get the existing transaction (Checks ownership - raises 404)
        db_transaction = await get_single_transaction(
            session=session,
            transaction_id=transaction_id,
            user_id=user_id,
        )

        # 2. Check for immutable fields being updated
        update_data = transaction_update.model_dump(exclude_unset=True)
        if 'amount' in update_data or 'transaction_type' in update_data or 'account_id' in update_data:
             app_logger.warning(
                msg=f'User {user_id} attempted to update immutable field on transaction {transaction_id}'
            )
             raise HTTPException(
                 status_code=status.HTTP_400_BAD_REQUEST,
                 detail="Financial fields (amount, type, account) cannot be modified via update endpoint."
             )

        # 3. Apply updates using the repository
        updated_transaction = await transaction_repo.update_transaction(
            session=session,
            db_transaction=db_transaction,
            transaction_update=transaction_update,
        )

        app_logger.info(
            msg=f'Transaction {transaction_id} updated successfully'
        )

        return updated_transaction

    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        app_logger.error(
            msg=f'Server Error updating transaction {transaction_id}: {e}'
        )
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def remove_transaction(
    session: Session,
    transaction_id: int,
    user_id: int,
) -> None:
    """
    Deletes the transaction and reverses the effect on the account balance.
    """
    try:
        app_logger.info(
            msg=f'Request to delete transaction {transaction_id} for user {user_id}'
        )

        # 1. Get the transaction (Checks ownership - raises 404)
        db_transaction = await get_single_transaction(
            session=session,
            transaction_id=transaction_id,
            user_id=user_id,
        )

        # 2. Get associated account (Checks ownership - raises 404)
        account_to_update = await account_repo.get_account_by_id(
            session=session,
            account_id=db_transaction.account_id,
            user_id=user_id
        )

        if not account_to_update:
            # Database inconsistency error
            app_logger.error(
                msg=f'Consistency Error: Account {db_transaction.account_id} not found for transaction {transaction_id}'
            )
            raise HTTPException(
                detail="Associated Account not found. Cannot reverse balance.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # 3. Calculate the REVERSE balance change (checks for TRANSFER - raises 400)
        reverse_change = _calculate_balance_change(db_transaction, reverse=True)

        # 4. Apply the reverse change and commit account update (DELEGATED TO ACCOUNT REPOSITORY)
        await account_repo.update_account_balance(
            session=session,
            account=account_to_update,
            balance_change=reverse_change
        )

        # 5. Delete the transaction record (Repository call)
        await transaction_repo.delete_transaction(
            session=session,
            db_transaction=db_transaction,
        )
        
        app_logger.info(
            msg=f'Transaction {transaction_id} deleted and balance reversed successfully'
        )

    except HTTPException as e:
        session.rollback()
        raise e
    except Exception as e:
        session.rollback()
        app_logger.error(
            msg=f'Server Error deleting transaction {transaction_id}: {e}'
        )
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    