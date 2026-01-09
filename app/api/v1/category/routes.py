from typing import List

from fastapi import APIRouter, status, Depends
from app.api import deps as global_deps # For SessionDep and CurrentUserDep

from app.api.v1.category import (
    schemas as category_schemas,
    service as category_service,
)


router = APIRouter(prefix='/categories', tags=['Categories'])


# --- POST: Create Category ---

@router.post(
    path='',
    status_code=status.HTTP_201_CREATED,
    response_model=category_schemas.CategoryRead,
)
async def create_category_route(
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
    category_in: category_schemas.CategoryCreate,
):
    """
    Creates a new custom category for the current user.
    """
    return await category_service.create_new_category(
        session=session,
        category_in=category_in,
        user_id=current_user.id,
    )


# --- GET: List All User/System Categories ---

@router.get(
    path='',
    status_code=status.HTTP_200_OK,
    response_model=List[category_schemas.CategoryRead],
)
async def read_categories_route(
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
):
    """
    Retrieves all categories available to the user (custom + system-defined).
    """
    return await category_service.get_list_categories(
        session=session,
        user_id=current_user.id,
    )


# --- GET: Get Single Category ---

@router.get(
    path='/{category_id}',
    status_code=status.HTTP_200_OK,
    response_model=category_schemas.CategoryRead,
)
async def read_single_category_route(
    category_id: int,
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
):
    """
    Retrieves a specific category by ID.
    """
    return await category_service.get_single_category(
        session=session,
        category_id=category_id,
        user_id=current_user.id,
    )


# --- PUT/PATCH: Update Category (Name/System Name) ---

# @router.patch(
#     path='/{category_id}',
#     status_code=status.HTTP_200_OK,
#     response_model=category_schemas.CategoryRead,
# )
# async def update_category_route(
#     category_id: int,
#     session: global_deps.SessionDep,
#     current_user: global_deps.CurrentUserDep,
#     category_update: category_schemas.CategoryCreate, # Reusing for update fields
# ):
#     """
#     Updates the name or system_name of a custom category. System categories are immutable.
#     """
#     return await category_service.update_existing_category(
#         session=session,
#         category_id=category_id,
#         category_update=category_update,
#         user_id=current_user.id,
#     )


# # --- DELETE: Delete Category ---

# @router.delete(
#     path='/{category_id}',
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# async def delete_category_route(
#     category_id: int,
#     session: global_deps.SessionDep,
#     current_user: global_deps.CurrentUserDep,
# ):
#     """
#     Deletes a custom category. Fails if it is a system category or has linked transactions.
#     """
#     return await category_service.remove_category(
#         session=session,
#         category_id=category_id,
#         user_id=current_user.id,
#     )
