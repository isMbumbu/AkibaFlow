from pydantic import BaseModel, EmailStr
from datetime import datetime

# Used for POST /api/v1/auth/signup (request)
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Used for GET /api/v1/user/me (response)
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
