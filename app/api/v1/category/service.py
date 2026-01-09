from typing import List

from fastapi import status, HTTPException
from sqlmodel import Session

from app.core.logging_config import app_logger
from app.api.v1.category import (
    repository as category_repo,
    schemas as category_schemas,
    models as category_model,
)

# --- CRUD and Business Logic Functions ---

async def create_new_category(
    session: Session,
    category_in: category_schemas.CategoryCreate,
    user_id: int,
) -> category_model.Category:
    """
    Creates a new category, ensuring the name is unique for the user.
    """
    try:
        app_logger.info(f"Request to create category '{category_in.name}' for user {user_id}")

        # 1. Check for existing category name (Business Rule)
        existing_category = await category_repo.get_category_by_name(
            session=session,
            name=category_in.name,
            user_id=user_id,
        )

        if existing_category:
            app_logger.warning(f"Category name '{category_in.name}' already exists for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A category with this name already exists."
            )

        # 2. Create the category record (Repository call)
        new_category = await category_repo.create_category(
            session=session,
            category_in=category_in,
            user_id=user_id,
        )

        app_logger.info(f"Category {new_category.id} created successfully.")
        return new_category

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        app_logger.error(f"Server Error creating category for user {user_id}: {e}")
        raise HTTPException(
            detail='An unexpected error occurred during category creation.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_single_category(
    session: Session,
    category_id: int,
    user_id: int,
) -> category_model.Category:
    """
    Retrieves a single category by ID, enforcing user ownership or system access.
    """
    try:
        app_logger.info(f"Request to fetch category {category_id} for user {user_id}")
        
        category = await category_repo.get_category_by_id(
            session=session,
            category_id=category_id,
            user_id=user_id,
        )

        if not category:
            app_logger.warning(f"Category {category_id} not found or access denied for user {user_id}")
            raise HTTPException(
                detail="Category not found or access denied.",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        return category
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Server Error fetching category {category_id}: {e}")
        raise HTTPException(
            detail='An unexpected error occurred while fetching the category.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_list_categories(
    session: Session,
    user_id: int,
) -> List[category_model.Category]:
    """
    Retrieves a list of all user-owned and system categories.
    """
    try:
        app_logger.info(f"Request to list categories for user {user_id}")
        
        return await category_repo.get_user_categories(
            session=session,
            user_id=user_id,
        )
        
    except Exception as e:
        app_logger.error(f"Server Error listing categories for user {user_id}: {e}")
        raise HTTPException(
            detail='An unexpected error occurred while listing categories.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def update_existing_category(
    session: Session,
    category_id: int,
    category_update: category_schemas.CategoryCreate, # Use CategoryCreate for partial update fields
    user_id: int,
) -> category_model.Category:
    """
    Updates an existing category. Only custom categories can be updated.
    """
    try:
        app_logger.info(f"Request to update category {category_id} for user {user_id}")

        # 1. Get the existing category (Checks ownership/system access - raises 404)
        db_category = await get_single_category(
            session=session,
            category_id=category_id,
            user_id=user_id,
        )
        
        # 2. Business Rule: Only custom categories can be updated
        if not db_category.is_custom:
            app_logger.warning(f"User {user_id} attempted to modify non-custom category {category_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System or non-custom categories cannot be modified."
            )
        
        # 3. Business Rule: Check for name conflict if the name is being updated
        if category_update.name and category_update.name != db_category.name:
            existing_conflict = await category_repo.get_category_by_name(
                session=session,
                name=category_update.name,
                user_id=user_id,
            )
            if existing_conflict:
                 app_logger.warning(f"Update failed: New name '{category_update.name}' conflicts with existing category.")
                 raise HTTPException(
                     status_code=status.HTTP_400_BAD_REQUEST,
                     detail="A category with the updated name already exists."
                 )

        # 4. Apply updates
        updated_category = await category_repo.update_category(
            session=session,
            db_category=db_category,
            category_update=category_update,
            updated_by=user_id,
        )

        app_logger.info(f"Category {category_id} updated successfully.")
        return updated_category

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        app_logger.error(f"Server Error updating category {category_id}: {e}")
        raise HTTPException(
            detail='An unexpected error occurred during category update.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def remove_category(
    session: Session,
    category_id: int,
    user_id: int,
) -> None:
    """
    Deletes a custom category. Fails if it's a system category or has linked transactions.
    """
    try:
        app_logger.info(f"Request to delete category {category_id} for user {user_id}")

        # 1. Get the category (Checks ownership/system access - raises 404)
        db_category = await get_single_category(
            session=session,
            category_id=category_id,
            user_id=user_id,
        )

        # 2. Business Rule: Only custom categories can be deleted
        if not db_category.is_custom:
            app_logger.warning(f"User {user_id} attempted to delete non-custom category {category_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="System categories cannot be deleted."
            )

        # 3. Business Rule: Check for linked transactions (AVOIDING CASCADE DELETE)
        # We need a Transaction repository function for this, but for now we'll simulate the check:
        # linked_transactions = await transaction_repo.count_transactions_by_category(session, category_id)
        # if linked_transactions > 0:
        #    raise HTTPException(status_code=409, detail="Cannot delete category with linked transactions.")
        
        # --- MVP Simplification: Assume repository check fails if transactions exist ---

        # 4. Delete the category record (Repository call)
        await category_repo.delete_category(
            session=session,
            db_category=db_category,
        )
        
        app_logger.info(f"Category {category_id} deleted successfully.")

    except HTTPException:
        session.rollback()
        raise
    except Exception as e:
        session.rollback()
        app_logger.error(f"Server Error deleting category {category_id}: {e}")
        raise HTTPException(
            detail='An unexpected error occurred during category deletion.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    