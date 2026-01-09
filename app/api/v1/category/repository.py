from typing import List, Optional

from sqlmodel import Session, select
from app.api.v1.category import (
    models as category_model,
    schemas as category_schema,
)

# --- Standard CRUD Functions ---

async def create_category(
    session: Session,
    category_in: category_schema.CategoryCreate,
    user_id: int,
) -> category_model.Category:
    """
    Creates a new category for a specific user.
    """
    # 1. Prepare data for model instantiation
    category_data = category_in.model_dump()
    
    # 2. Check if the category being created is one of the default system names
    # If a system_name is provided in the input, it is NOT custom.
    is_custom = category_in.system_name is None
    
    # 3. Create Category instance
    category_obj = category_model.Category.model_validate(
        category_in,
        update={
            "user_id": user_id,
            "created_by": user_id,
            "is_custom": is_custom,
        },
    )

    # 4. Persist to DB
    session.add(category_obj)
    session.commit()
    session.refresh(category_obj)
    
    return category_obj


async def get_category_by_id(
    session: Session, 
    category_id: int,
    user_id: int, 
) -> category_model.Category | None:
    """
    Fetches a specific category, enforcing ownership (user_id).
    System-created categories (user_id=None) are also accessible.
    """
    statement = (
        select(category_model.Category)
        .where(category_model.Category.id == category_id)
        # OR condition allows access to user-owned categories OR system categories
        .where(
            (category_model.Category.user_id == user_id) | 
            (category_model.Category.user_id.is_(None))
        )
    )
    category = session.exec(statement).first()
    
    return category


async def get_user_categories(
    session: Session,
    user_id: int,
) -> List[category_model.Category]:
    """
    Fetches all user-owned categories PLUS all system-defined categories.
    """
    statement = (
        select(category_model.Category)
        # Filters for categories owned by the user OR system categories (user_id IS NULL)
        .where(
            (category_model.Category.user_id == user_id) | 
            (category_model.Category.user_id.is_(None))
        )
        .order_by(category_model.Category.name)
    )
    categories = session.exec(statement).all()
    
    return list(categories)


async def update_category(
    session: Session,
    db_category: category_model.Category,
    category_update: category_schema.CategoryCreate, # Reusing CategoryCreate for update fields
    updated_by: int,
) -> category_model.Category:
    """
    Updates the category record. Only custom categories can be updated.
    """
    # 1. Populate the ORM model with new values
    update_data = category_update.model_dump(exclude_unset=True)
    update_data['updated_by'] = updated_by

    # Update the ORM object
    db_category.model_validate(
        update_data, 
        update=update_data
    )
    
    # 2. Persist the changes
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    
    return db_category


async def delete_category(
    session: Session,
    db_category: category_model.Category,
) -> None:
    """
    Deletes a category from the database.
    """
    session.delete(db_category)
    session.commit()
    
    
async def get_category_by_name(
    session: Session, 
    name: str,
    user_id: int, 
) -> category_model.Category | None:
    """
    Checks if a category name already exists for the user (or as a system name).
    """
    statement = (
        select(category_model.Category)
        .where(category_model.Category.name == name)

        .where(
            (category_model.Category.user_id == user_id) | 
            (category_model.Category.user_id.is_(None))
        )
    )
    category = session.exec(statement).first()
    
    return category
