from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.db.base import Base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship # Used for relationships

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Relationships (e.g., a user has many accounts)
    # accounts = relationship("Account", back_populates="owner")
