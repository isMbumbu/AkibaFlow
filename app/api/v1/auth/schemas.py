from typing import Optional
from datetime import datetime, date

from sqlmodel import SQLModel


class Token(SQLModel):
    """ JSON payload containing access token """
    access_token: str
    token_type: str = 'bearer'


class TokenPayload(SQLModel):
    """ JSON payload containing user ID and optional subject """
    sub: str | None = None


class UserRead(SQLModel):
    """ For reading a user details (GET responses) """
    id: int
    first_name: str
    last_name: str
    email: str | None = None
    phone_number: str | None = None
    active: bool

    created_at: datetime
    updated_at: datetime | None = None