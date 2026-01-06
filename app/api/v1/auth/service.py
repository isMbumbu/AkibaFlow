from typing import Annotated
from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status, APIRouter, Depends, HTTPException

from app.core import security
from app.api.deps import SessionDep, current_active_user
from app.core.config import settings
from app.api.v1.user.models import User
from app.core.logging_config import app_logger

from app.api.v1.user import (
    repository as user_repository)

from app.api.v1.auth import (
    schemas as auth_schemas, utils as auth_utils)

router = APIRouter(tags=['Auth'])


@router.post('/login', response_model=auth_schemas.Token)
async def login(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> auth_schemas.Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    try:
        app_logger.info(msg=f'New login request from: {form_data.username}')

        # Login with email
        if '@' in form_data.username:
            user = await auth_utils.authenticate_with_email(
                session=session,
                email=form_data.username,
                password=form_data.password,
            )

        # Check if login was successful
        if not user:
            # Log handled in utils file
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Incorrect username or password',
            )

        # Check if user is active
        if not user.active:
            app_logger.warning(
                msg=f'Failed to login user: {form_data.username} - User is inactive'
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Inactive user'
            )

        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        access_token = await security.create_access_token(
            subject=user.id,
            expires_delta=access_token_expires,
        )

        app_logger.info(msg=f'Successfully logged in user: {user.email}')

        await auth_utils.update_user_login_details(
            session=session, db_user=user, action_type='login')

        return auth_schemas.Token(
            access_token=access_token, token_type='bearer')

    except HTTPException as e:
        app_logger.error(
            msg=f'Error loggin in user: {form_data.username}: {e.detail}')
        raise HTTPException(
            detail=e.detail,
            status_code=e.status_code,
        )
    except Exception as e:
        session.rollback() 
        app_logger.error(msg=f'Server Error loggin in user: {form_data.username}: {e}')
        raise HTTPException(
            detail=f'An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.get('/whoami', response_model=auth_schemas.UserRead)
async def whoami(
    session: SessionDep, current_user: Annotated[User, Depends(current_active_user)]
):
    """
    Method to get the current user details (Simplified)
    """
    try:
        results = auth_schemas.UserRead(
            **current_user.model_dump(include={
                'id', 
                'first_name', 
                'last_name', 
                'email', 
                'phone_number', 
                'active',
                'created_at',
                'updated_at',
            }),

        )

        return results
    except HTTPException as e:
        app_logger.error(
            msg=f'Error processing whoami {current_user.id}: {e.detail}')
        raise HTTPException(
            detail=e.detail,
            status_code=e.status_code,
        )
    except Exception as e:
        session.rollback()
        app_logger.error(
            msg=f'Server Error processing whoami {current_user.id}: {e}')
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )