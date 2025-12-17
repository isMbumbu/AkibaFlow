from typing import Generator
from fastapi import Depends
from app.core.db.session import get_db
from sqlalchemy.orm import Session


def get_db_session() -> Generator[Session, None, None]:
    yield from get_db()
    
# Dependency for authorization (will be implemented in Auth layer)
# def get_current_user(db: Session = Depends(get_db_session)):
#     # Logic to decode JWT, fetch user from DB, and check active status
#     pass
