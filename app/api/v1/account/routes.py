# app/api/v1/account/routes.py

from fastapi import APIRouter, Depends, status

from app.api import deps as global_deps
from app.api.v1.account import (
    schemas as account_schemas, 
    service as account_service
)

# Define the router with its prefix and tag
router = APIRouter(prefix='/accounts', tags=['Accounts'])


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=account_schemas.AccountRead,
)
async def create_account(
    session: global_deps.SessionDep,
    account_in: account_schemas.AccountCreate,
    current_user: global_deps.CurrentUserDep,
):
    """Route to create a new account."""
    return await account_service.create_account(
        session=session,
        account_in=account_in,
        current_user=current_user,
    )


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=list[account_schemas.AccountRead],
)
async def get_all_user_accounts(
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
):
    """Route to retrieve all active accounts for the authenticated user."""
    return await account_service.get_all_user_accounts(
        session=session,
        current_user=current_user,
    )


@router.patch(
    '/{account_id}',
    status_code=status.HTTP_200_OK,
    response_model=account_schemas.AccountRead,
)
async def update_account_details(
    session: global_deps.SessionDep,
    account_id: int,
    account_update: account_schemas.AccountUpdate,
    current_user: global_deps.CurrentUserDep,
):
    """Route to update account details by ID."""
    return await account_service.update_account_details(
        session=session,
        account_id=account_id,
        account_update=account_update,
        current_user=current_user,
    )


@router.get(
    '/{account_id}',
    status_code=status.HTTP_200_OK,
    response_model=account_schemas.AccountRead,
)
async def get_account_details(
    session: global_deps.SessionDep,
    account_id: int,
    current_user: global_deps.CurrentUserDep,
):
    """Route to retrieve account details by ID."""
    return await account_service.get_account_details(
        session=session,
        account_id=account_id,
        current_user=current_user,
    )


@router.delete(
    '/{account_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_account(
    session: global_deps.SessionDep,
    account_id: int,
    current_user: global_deps.CurrentUserDep,
):
    """Route to delete (deactivate) an account by ID."""
    await account_service.delete_account(
        session=session,
        account_id=account_id,
        current_user=current_user,
    )
    return None

