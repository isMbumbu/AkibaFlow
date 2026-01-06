"""
Script to create a superuser for AkibaFlow using environment variables.
Usage: python scripts/create_superuser.py
"""

import sys
import os
import asyncio # <--- ADDED: Import asyncio for running async functions
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlmodel import Session, select
from app.core.db import engine
from app.api.v1.user.models import User
from app.core.security import get_password_hash
from app.core.config import settings

# 1. RENAME and DEFINE as an ASYNC function
async def async_create_superuser():
    # Use SQLModel Session context manager
    with Session(engine) as db:
        try:
            # Use SQLModel select statement
            statement = select(User).where(User.is_superuser == True)
            superuser = db.exec(statement).first()
            
            if superuser:
                print(f"Superuser already exists: {superuser.email}")
                return

            # Get superuser credentials from environment
            email = os.getenv("FIRST_SUPERUSER_EMAIL", settings.FIRST_SUPERUSER_EMAIL)
            password = os.getenv("FIRST_SUPERUSER_PASSWORD", settings.FIRST_SUPERUSER_PASSWORD)

            if not email or not password:
                print("FIRST_SUPERUSER_EMAIL and FIRST_SUPERUSER_PASSWORD must be set in environment variables.")
                return

            # Check if user already exists
            statement = select(User).where(User.email == email)
            existing_user = db.exec(statement).first()
            if existing_user:
                print(f"User with email {email} already exists.")
                return

            # 2. 'await' is now valid inside this async function
            hashed_password = await get_password_hash(password)
            
            # Note: We must include first_name and last_name as they are required fields in the model
            superuser = User(
                email=email,
                hashed_password=hashed_password,
                is_superuser=True,
                active=True,
                first_name="Admin",
                last_name="User",
                # Set phone_number if required, assuming it's optional for superuser creation here
            )

            db.add(superuser)
            db.commit()
            db.refresh(superuser)

            print(f"Superuser created successfully: {superuser.email}")

        except Exception as e:
            # Added sys.exit(1) to fail the startup if superuser creation fails
            print(f"Error creating superuser: {e}")
            db.rollback()
            sys.exit(1)


if __name__ == "__main__":
    # 3. Use asyncio.run() to execute the async function
    asyncio.run(async_create_superuser())