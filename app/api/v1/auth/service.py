from typing import Annotated
from datetime import timedelta

from fastapi.security import OAuth2PasswordRequestForm
from fastapi import status, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse 

from app.core import security
from app.api.deps import SessionDep, current_active_user
from app.core.config import settings
from app.api.v1.user.models import User
from app.core.logging_config import app_logger

from app.api.v1.user import (
    repository as user_repository)

from app.api.v1.user import schemas as user_schemas 
from app.api.deps import SessionDep

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


@router.post(
    '/register',
    status_code=status.HTTP_202_ACCEPTED, 
)
async def register(
    session: SessionDep,
    user_in: user_schemas.UserRegister,
) -> JSONResponse:
    """
    Service function to handle secure user registration logic, 
    setting the user to inactive for required verification.
    """
    try:
        app_logger.info(msg=f'New registration request for: {user_in.email or user_in.phone_number}')

        # --- 1. PRE-CHECKS & VALIDATION ---
        
        # Check if user already exists by Email
        if user_in.email:
            existing_user = await user_repository.get_user_by_email(session=session, user_email=user_in.email)
            if existing_user:
                app_logger.warning(f"Registration failed: Email '{user_in.email}' already exists.")
                # Use a generic message to prevent enumeration attacks
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Account with this email already exists.")
        
        # Check if user already exists by Phone Number
        if user_in.phone_number:
            existing_user = await user_repository.get_user_by_phone(session=session, user_phone=user_in.phone_number)
            if existing_user:
                app_logger.warning(f"Registration failed: Phone '{user_in.phone_number}' already exists.")
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Account with this phone number already exists.")


        # --- 2. USER CREATION ---
        
        # Map UserRegister to UserCreate, enforcing internal safety defaults
        user_create_data = user_schemas.UserCreate(
            first_name=user_in.first_name,
            last_name=user_in.last_name,
            email=user_in.email,
            phone_number=user_in.phone_number,
            password=user_in.password,
            is_superuser=False,
            active=False,
        )

        new_user = await user_repository.create_user(session=session, user_create=user_create_data)

        # --- 3. POST-CREATION (Verification Setup) ---
        
        # TODO: Trigger Celery/BackgroundTask to send verification email/SMS
        # from fastapi import BackgroundTasks
        # background_tasks.add_task(auth_utils.send_verification_email, new_user.id) 
        
        app_logger.info(f"Successfully registered user ID: {new_user.id}. Pending activation.")

        # --- 4. SUCCESS RESPONSE ---
        return JSONResponse(
            status_code=status.HTTP_202_ACCEPTED,
            content={
                "message": "Registration successful. Please check your email/phone for the verification link/code to activate your account."
            }
        )

    except HTTPException:
        # Re-raise explicit HTTP exceptions
        raise
    except Exception as e:
        session.rollback()
        error_target = user_in.email or user_in.phone_number or "unknown"
        app_logger.error(msg=f'Server Error registering user: {error_target}: {e}')
        raise HTTPException(
            detail='An unexpected error occurred during registration. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
