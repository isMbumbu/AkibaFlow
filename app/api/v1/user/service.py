from fastapi import status, HTTPException

from app.api.deps import SessionDep
from app.core.logging_config import app_logger
from app.api.v1.user import (
    schemas as user_schemas, repository as user_repository)


async def get_all_users(
    session: SessionDep,
    offset: int = 0,
    limit: int = 100,
):
    """
    Retrieve all users from the database (paginated).

    Args:
    -----
        session: The database session to use.
        limit: Maximum number of records to return.
        offset: Number of records to skip.

    Returns:
    --------
        list[User]: A list of users records.

    Raises:
    -------
        Exception: If there is an error during retrieval.
    """
    try:
        app_logger.info(
            msg='New request to get all users.')

        # Removed is_agent parameter
        return await user_repository.get_all_users(
            session=session, offset=offset, limit=limit)

    except HTTPException as e:
        app_logger.error(msg=f'Error retrieving users: {e.detail}')
        raise HTTPException(
            detail=e.detail,
            status_code=e.status_code,
        )
    except Exception as e:
        session.rollback()
        app_logger.error(
            msg=f'Server Error retrieving users: {e}')
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def search_users(
    session: SessionDep,
    query: str,
    offset: int = 0,
    limit: int = 100,
) -> list[user_schemas.UserRead]:
    """
    Search users by email, phone number, or full name (paginated).

    Args:
    -----
        session: The database session to use.
        query: Search term (email, phone_number, or name).
        offset: Records to skip.
        limit: Max records to return.

    Returns:
    --------
        list[UserRead]: Matching user records.

    Raises:
    -------
        HTTPException: If there is an error during search.
        Exception: If there is an unexpected error.
    """
    try:
        # Simplified logging
        app_logger.info(
            msg=f'New request to search users with query: "{query}"')

        return await user_repository.search_users(
            session=session,
            query=query,
            offset=offset,
            limit=limit,
        )

    except HTTPException as e:
        app_logger.error(msg=f'Error searching users: {e.detail}')
        raise HTTPException(
            detail=e.detail,
            status_code=e.status_code,
        )
    except Exception as e:
        session.rollback()
        app_logger.error(
            msg=f'Server Error searching users: {e}')
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def get_user_by_id(
    session: SessionDep,
    user_id: int,
) -> user_schemas.UserRead:
    """
    Fetch a user in the database based on its ID.

    Args:
    -----
        session: The database session to use.
        user_id: The ID of the user.

    Returns:
    --------
        UserRead: The user object if found, NotFound Error if not found.

    Raises:
    -------
        HTTPException: If there is an error during retrieval.
        Exception: If there is an unexpected error.
    """
    try:
        app_logger.info(
                msg=f'Request to fetch user with ID: {user_id}')

        fetched_user = await user_repository.get_user_by_id(
                        session=session, user_id=user_id)

        if not fetched_user:
            app_logger.warning(
                msg=f'User not found with ID: {user_id}')
            raise HTTPException(
                detail='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Removed company relationship retrieval logic
        # user_companies = await user_repository.get_user_companies(...)
        # result = user_schemas.UserReadDetailed(**fetched_user.model_dump())
        # result.user_companies = user_companies

        # Return the basic UserRead model
        return fetched_user

    except HTTPException as e:
        app_logger.error(
            msg=f'Error fetching user {user_id}: {e.detail}')
        raise HTTPException(
            detail=e.detail,
            status_code=e.status_code,
        )
    except Exception as e:
        session.rollback()
        app_logger.error(
            msg=f'Server Error fetching user {user_id}: {e}')
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def create_user(
    session: SessionDep,
    created_by: int,
    user_sch: user_schemas.UserCreate,
) -> user_schemas.UserRead:
    """
    Create a new user in the database.

    Args:
    -----
        session: The database session to use.
        user_sch: The user schema to create.
        created_by: The ID of the logged in user creating the user.

    Returns:
    --------
        User: The created user object.

    Raises:
    -------
        HTTPException: If there is a user error during creation.
        Exception: If there is an unexpected error.
    """
    try:
        app_logger.info(msg=f'Request to create a new user')

        # Removed company existence check (comp_exists)

        if await user_repository.get_user_by_email(
            session=session, user_email=user_sch.email):
            app_logger.warning(
                msg=f'User already exists with email: {user_sch.email}')
            raise HTTPException(
                detail='A user with the email already exists.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if await user_repository.get_user_by_phone(
            session=session, user_phone=user_sch.phone_number):
            app_logger.warning(
                msg=f'User already exists with phone number: {user_sch.phone_number}')
            raise HTTPException(
                detail='A user with the phone number already exists.',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Build the final UserCreate model directly from the input schema
        user_details = user_schemas.UserCreate(
            **user_sch.model_dump(), created_by=created_by)

        created_user = await user_repository.create_user(
                        session=session, user_create=user_details)

        # Removed user company link creation logic

        app_logger.info(msg=f'New user created with ID: {created_user.id}')

        return await get_user_by_id(
            session=session, user_id=created_user.id)

    except HTTPException as e:
        app_logger.error(msg=f'Error creating user: {e.detail}')
        raise HTTPException(
            detail=e.detail,
            status_code=e.status_code,
        )
    except Exception as e:
        session.rollback()
        app_logger.error(msg=f'Server Error creating user: {e}')
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


async def update_user(
    session: SessionDep,
    user_id: int,
    updated_by: int,
    user_sch: user_schemas.UserUpdateReq,
) -> user_schemas.UserRead:
    """
    Update an existing user in the database.

    Args:
    -----
        session: The database session to use.
        user_id: The ID of the user to update.
        updated_by: The ID of the user updating the user.
        user_sch: The user schema with updated data.

    Returns:
    --------
        User: The updated user object.

    Raises:
    -------
        HTTPException: If there is a user error during update.
        Exception: If there is an unexpected error.
    """
    try:
        app_logger.info(
                msg=f'New request to update user with ID: {user_id}')

        db_user = await user_repository.get_user_by_id(
                                session=session, user_id=user_id)

        if not db_user:
            app_logger.warning(
                msg=f'User not found with ID: {user_id}')
            raise HTTPException(
                detail='User not found.',
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # Removed check for user_sch.company_id and company existence check

        user_details = user_schemas.UserUpdate(
                                    **db_user.model_dump())
        user_details.updated_by = updated_by

        for key, value in user_sch.model_dump(exclude_unset=True).items():
            setattr(user_details, key, value)

        updated_user = await user_repository.update_user(
                                    session=session,
                                    db_user=db_user,
                                    user_sch=user_details,
                                )

        app_logger.info(
            msg=f'User updated successfully with ID: {updated_user.id}')

        return await get_user_by_id(
            session=session, user_id=db_user.id)

    except HTTPException as e:
        app_logger.error(
            msg=f'Error updating user {user_id}: {e.detail}')
        raise HTTPException(
            detail=e.detail,
            status_code=e.status_code,
        )
    except Exception as e:
        session.rollback()
        app_logger.error(
            msg=f'Server Error updating user {user_id}: {e}')
        raise HTTPException(
            detail='An unexpected error occurred. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
