from typing import Annotated
from collections.abc import Generator

import jwt

from sqlmodel import Session
from pydantic import ValidationError
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from app.core import security
from app.core.db import engine
from app.core.config import settings
from app.api.v1.user.models import User
from app.core.logging_config import app_logger


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f'{settings.API_VERSION_STR}/auth/login'
)


def get_db() -> Generator[Session, None, None]:
    """
    Method to get the current database session.

    Args:
    -----
        None

    Returns:
    --------
        A generator that yields a database session.

    Raises:
    -------
        None
    """

    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def current_active_user(session: SessionDep, token: TokenDep):
    """"
    Method to get the current user from the access token.

    Args:
    -----
        session (SessionDep): The current database session.
        token (TokenDep): The access token.

    Returns:
    -------
        User: The current user object.

    Raises:
    -------
        HTTPException: If the token is invalid or the user is not found.
        HTTPException: If the user is inactive.
    """

    try:
        app_logger.info('Attempting to validate token')

        # Import here to avoid circular imports
        from app.api.v1.auth.schemas import TokenPayload

        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )

        token_data = TokenPayload(**payload)

        user = session.get(User, token_data.sub)

        if not user:
            app_logger.error(f'User not found for token: {token}')
            raise HTTPException(
                status_code=404, detail='User not found')

        if not user.active:
            app_logger.warning(f'Inactive user {user.email} tried logging in')
            raise HTTPException(
                status_code=400, detail='Inactive user')
        
        app_logger.info(f'User found: {user.email}')

        return user

    except (InvalidTokenError, ValidationError):
        app_logger.error(f'Invalid token or payload {token}')
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials',
        )


CurrentUserDep = Annotated[User, Depends(current_active_user)] # FIXED ALIAS NAME


def get_current_active_superuser(current_user: CurrentUserDep) -> User: # USING NEW ALIAS
    """
    Method to get the current active superuser.

    Args:
    -----
        current_user (CurrentUserDep): The current user object.

    Returns:
    -------
        User: The current active superuser object.

    Raises:
    -------
        HTTPException: If the user is not a superuser.
    """
    app_logger.info(f'Checking if user {current_user.email} is a superuser')

    if not current_user.is_superuser:
        app_logger.warning(f'User {current_user.email} is not a superuser')
        raise HTTPException(
            status_code=403,
            detail='The user does not have enough privileges',
        )

    app_logger.info(f'User {current_user.email} is using superuser access')

    return current_user
    