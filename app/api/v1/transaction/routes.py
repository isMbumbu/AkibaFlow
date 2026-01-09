from typing import List

from fastapi import APIRouter, Depends, status, Query

from app.api import deps as global_deps
from app.api.v1.transaction import (
    schemas as transaction_schemas,
    service as transaction_service,
)


router = APIRouter(prefix='/transactions', tags=['Transactions'])


# --- POST: Create Transaction ---

@router.post(
    path='',
    status_code=status.HTTP_201_CREATED,
    response_model=transaction_schemas.TransactionRead,
)
async def create_transaction_route(
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
    transaction_in: transaction_schemas.TransactionCreate,
):
    """
    Creates a new transaction (INCOME/EXPENSE) and updates the account balance.
    All error handling and logic are handled by the service layer.
    """
    return await transaction_service.create_new_transaction(
        session=session,
        transaction_in=transaction_in,
        user_id=current_user.id,
    )


# --- GET: List All User Transactions ---

@router.get(
    path='',
    status_code=status.HTTP_200_OK,
    response_model=List[transaction_schemas.TransactionRead],
)
async def read_transactions_route(
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
    skip: int = Query(0, description="Number of items to skip"),
    limit: int = Query(100, description="Max number of items to return"),
):
    """
    Retrieves a paginated list of all transactions belonging to the current user.
    """
    return await transaction_service.get_list_transactions(
        session=session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
    )


# --- GET: Get Single Transaction ---

@router.get(
    path='/{transaction_id}',
    status_code=status.HTTP_200_OK,
    response_model=transaction_schemas.TransactionRead,
)
async def read_single_transaction_route(
    transaction_id: int,
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
):
    """
    Retrieves a specific transaction by ID, enforcing user ownership.
    """
    return await transaction_service.get_single_transaction(
        session=session,
        transaction_id=transaction_id,
        user_id=current_user.id,
    )


# --- PATCH: Update Transaction (Non-Financial) ---

@router.patch(
    path='/{transaction_id}',
    status_code=status.HTTP_200_OK,
    response_model=transaction_schemas.TransactionRead,
)
async def update_transaction_route(
    transaction_id: int,
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
    transaction_update: transaction_schemas.TransactionUpdateReq,
):
    """
    Updates non-financial fields (description, category) of a transaction.
    Financial fields (amount, type) are immutable via this endpoint.
    """
    return await transaction_service.update_transaction(
        session=session,
        transaction_id=transaction_id,
        transaction_update=transaction_update,
        user_id=current_user.id,
    )


# --- DELETE: Delete Transaction ---

@router.delete(
    path='/{transaction_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_transaction_route(
    transaction_id: int,
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
):
    """
    Deletes a transaction and reverses the effect on the associated account's balance.
    """
    return await transaction_service.remove_transaction(
        session=session,
        transaction_id=transaction_id,
        user_id=current_user.id,
    )
