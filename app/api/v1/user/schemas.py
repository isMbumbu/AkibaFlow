from typing import Optional
from datetime import datetime

from pydantic import EmailStr
from sqlmodel import Field, SQLModel

class UserBase(SQLModel):
    """ The base model for an app user, defining core, shared fields. """

    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    email: EmailStr | None = Field(
        unique=True, index=True, max_length=255, default=None)

    active: bool = True
    
    user_type: str | None = Field(default='user')
    
    phone_number: str | None = Field(max_length=15, default=None)
    

class UserCreate(UserBase):
    """ Schema for creating a new user (usually by an admin). """
    is_superuser: bool = False
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    """ Schema for self-registration. """
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    phone_number: str = Field(max_length=20)
    email: EmailStr | None = Field(default=None, max_length=255)


class UserLoginUpdate(SQLModel):
    """ JSON payload to update user details during login """
    last_login: datetime | None = None
    hashed_password: str | None = None


class UserRead(UserBase):
    """ For reading a user details (GET responses). """
    id: int
    
    # Minimal audit fields
    created_by: int | None = None
    updated_by: int | None = None
    created_at: datetime
    updated_at: datetime | None = None
    
  
class UserUpdateReq(SQLModel):
    """ For updating user info (PATCH). """
    first_name: str | None = None
    last_name: str | None = None
    user_type: str | None = None
    phone_number: str | None = None
    active: bool | None = None


class UserUpdate(UserBase):
    """ For updating user info internally (e.g., in a service layer). """
    active: bool | None = None
    updated_by: int | None = None
    