from typing import Any
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


ALGORITHM = 'HS256'


async def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    """
    Create a new access token.

    Args:
    ----
        subject: The subject for the token, typically a user ID or username.
        expires_delta: The duration for which the token will be valid.

    Returns:
    -------
        A JWT token as a string.

    Raises:
    ------
        ValueError: If the subject is not provided or expires_delta is not a timedelta.
    """

    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {'exp': expire, 'sub': str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.

    Args:
    ----
        plain_password: The plain password to verify.
        hashed_password: The hashed password to compare against.

    Returns:
    -------
        True if the passwords match, False otherwise.

    Raises:
    ------
        ValueError: If the plain_password or hashed_password is not provided.
        Exception: If there is an error during password verification.
    """

    return pwd_context.verify(
        secret=plain_password, hash=hashed_password)


async def get_password_hash(password: str) -> str:
    """
    Hash a plain password using bcrypt.

    Args:
    ----
        password: The plain password to hash.

    Returns:
    -------
        The hashed password as a string.

    Raises:
    ------
        ValueError: If the password is not provided.
        Exception: If there is an error during password hashing.
    """

    return pwd_context.hash(password)
