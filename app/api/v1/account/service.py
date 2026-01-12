
from typing import Annotated

from fastapi import status, APIRouter, Depends, HTTPException
from decimal import Decimal

from app.api.deps import SessionDep, current_active_user
from app.api.v1.user.models import User
from app.core.logging_config import app_logger

from app.api.v1.account import (
    schemas as account_schemas, 
    repository as account_repository
)


router = APIRouter(tags=['Accounts'])


def calculate_current_balance(account) -> account_schemas.AccountRead:
    """
    Helper to convert the ORM model to the Read schema, calculating the balance.
    Uses the stored current_balance if available, otherwise falls back to initial_balance.
    """
    # Use the updated current_balance from transactions, or initial_balance if not set
    current_balance = account.current_balance if account.current_balance is not None else account.initial_balance
    
    # Use model_validate to construct the AccountRead schema with the derived balance
    return account_schemas.AccountRead.model_validate(
        account,
        update={'current_balance': current_balance}
    )


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=account_schemas.AccountRead,
)
async def create_account(
    session: SessionDep,
    account_in: account_schemas.AccountCreate,
    current_user: Annotated[User, Depends(current_active_user)],
):
    """Creates a new financial account for the current user."""
    try:
        new_account = await account_repository.create_account(
            session=session,
            account_in=account_in,
            user_id=current_user.id,
        )
        return calculate_current_balance(new_account)
        
    except Exception as e:
        session.rollback()
        app_logger.error(f"Failed to create account for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during account creation."
        )


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=list[account_schemas.AccountRead],
)
async def get_all_user_accounts(
    session: SessionDep,
    current_user: Annotated[User, Depends(current_active_user)],
):
    """Retrieves all active accounts belonging to the current user."""
    try:
        accounts = await account_repository.get_user_accounts(
            session=session,
            user_id=current_user.id,
        )
        
        results = [calculate_current_balance(acc) for acc in accounts]
        return results
        
    except Exception as e:
        app_logger.error(f"Failed to retrieve accounts for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching accounts."
        )


@router.patch(
    '/{account_id}',
    status_code=status.HTTP_200_OK,
    response_model=account_schemas.AccountRead,
)
async def update_account_details(
    session: SessionDep,
    account_id: int,
    account_update: account_schemas.AccountUpdate,
    current_user: Annotated[User, Depends(current_active_user)],
):
    """Updates non-balance related details of a specific account."""
    try:
        # Use the detailed getter from the repository that includes the ownership check
        db_account = await account_repository.get_account_by_id(
            session=session,
            account_id=account_id,
            user_id=current_user.id,
        )
        
        if not db_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or access denied."
            )
            
        updated_account = await account_repository.update_account(
            session=session,
            db_account=db_account,
            account_update=account_update,
        )
        
        return calculate_current_balance(updated_account)

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        app_logger.error(f"Failed to update account {account_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during account update."
        )


@router.get(
    '/{account_id}',
    status_code=status.HTTP_200_OK,
    response_model=account_schemas.AccountRead,
)
async def get_account_details(
    session: SessionDep,
    account_id: int,
    current_user: Annotated[User, Depends(current_active_user)],
):
    """Retrieves details of a specific account by ID."""
    try:
        # Repository function that combines get_by_id and balance calculation
        account = await account_repository.get_account_details(
            session=session,
            account_id=account_id,
            user_id=current_user.id,
        )
        
        if not account:
            # Handle the case where the account was not found or ownership failed
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or access denied."
            )
        
        # Final conversion to the API schema
        return calculate_current_balance(account)
        
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Failed to retrieve account {account_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching account details."
        )


@router.delete(
    '/{account_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_account(
    session: SessionDep,
    account_id: int,
    current_user: Annotated[User, Depends(current_active_user)],
):
    """Deletes (deactivates) a specific account by ID."""
    try:
        # Check if account exists and is owned by the user (prevents 500 error on non-existent ID)
        account_exists = await account_repository.get_account_by_id(
            session=session,
            account_id=account_id,
            user_id=current_user.id,
        )
        
        if not account_exists:
            # Although a delete request usually returns 204 regardless, 404 is clearer here.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found or access denied."
            )
        
        # Use the repository function that performs the soft-delete via update statement
        await account_repository.delete_account(
            session=session,
            account_id=account_id,
            user_id=current_user.id,
        )
        
        return
    
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        app_logger.error(f"Failed to delete account {account_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during account deletion."
        )


@router.get(
    '/total-balance',
    status_code=status.HTTP_200_OK,
    response_model=dict,
)
async def get_total_balance(
    session: SessionDep,
    current_user: Annotated[User, Depends(current_active_user)],
):
    """Retrieves the total balance across all active accounts for the current user."""
    try:
        accounts = await account_repository.get_user_accounts(
            session=session,
            user_id=current_user.id,
        )
        
        total_balance = Decimal('0.00')
        for acc in accounts:
            account_read = calculate_current_balance(acc)
            total_balance += account_read.current_balance
        
        return {"total_balance": total_balance}
        
    except Exception as e:
        app_logger.error(f"Failed to calculate total balance for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while calculating total balance."
        )
