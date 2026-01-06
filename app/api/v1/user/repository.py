from sqlmodel import Session, select

from app.core.security import get_password_hash
from app.api.v1.user import (
    models as user_model, schemas as user_schema)


async def get_all_users(
    session: Session,
    limit: int = 100,
    offset: int = 0,
) -> list[user_model.User]:
    """
    Retrieve all active users with pagination.

    Args:
        session (Session): The database session.
        limit (int): Maximum number of records to return.
        offset (int): Number of records to skip.

    Returns:
        list[User]: A list of user records.
    """
    # Removed is_agent filter as the field was removed from the model
    statement = select(user_model.User).where(user_model.User.active == True)

    statement = (
        statement
        .offset(offset)
        .limit(limit)
    )
    users = session.exec(statement).all()

    return users


async def create_user(
    session: Session,
    user_create: user_schema.UserCreate
) -> user_model.User:
    """
    Create a new user in the database.

    Args:
    ----
        session: The database session to use.
        user_create:  The user data to create.

    Returns:
    -------
        The created user object.

    Raises:
    ------
        ValueError: If the user already exists.
        Exception: If there is an error during user creation.
    """

    hashed_password = await get_password_hash(user_create.password)

    user_obj = user_model.User.model_validate(
        user_create,
        update={"hashed_password": hashed_password},
    )

    session.add(user_obj)
    session.commit()
    session.refresh(user_obj)

    return user_obj


async def get_user_by_id(
        session: Session, user_id: int) -> user_model.User | None:
    """
    Fetch a user in the database based on their id

    Args:
    ----
        session: The database session to use.
        user_id:  The id of the user

    Returns:
    -------
        The user object if present None if not found

    Raises:
    ------
        Exception: If there is an error during execution
    """

    statement = (
        select(user_model.User)
        .where(user_model.User.id == user_id)
    )
    fetched_user = session.exec(statement).first()
    
    return fetched_user


async def get_user_by_email(
        session: Session, user_email: str) -> user_model.User | None: # Updated type hint to str
    """
    Fetch a user in the database based on their email

    Args:
    ----
        session: The database session to use.
        user_email:  The email of the user (now str)

    Returns:
    -------
        The user object if present None if not found

    Raises:
    ------
        Exception: If there is an error during execution
    """

    statement = (
        select(user_model.User)
        .where(user_model.User.email == user_email)
    )
    fetched_user = session.exec(statement).first()
    
    return fetched_user


async def get_user_by_phone(
        session: Session, user_phone: str) -> user_model.User | None: # Updated type hint to str
    """
    Fetch a user in the database based on their phone number

    Args:
    ----
        session: The database session to use.
        user_phone:  The phone number of the user (now str)

    Returns:
    -------
        The user object if present None if not found

    Raises:
    ------
        Exception: If there is an error during execution
    """

    statement = (
        select(user_model.User)
        .where(user_model.User.phone_number == user_phone)
    )
    fetched_user = session.exec(statement).first()

    return fetched_user


async def update_user_login_details(
    session: Session,
    db_user: user_model.User,
    user_sch: user_schema.UserLoginUpdate
) -> user_model.User:
    """
    Method to update user login details.

    Args:
    -----
        session (Session): The current database session.
        db_user (User): The user model to update.
        user_sch (UserUpdate): The user schema to update.

    Returns:
    -------
        User: The updated user object.

    Raises:
    -------
        None
    """

    user_data = user_sch.model_dump(exclude_unset=True)

    db_user.sqlmodel_update(user_data, update=user_data)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


async def update_user(
    session: Session,
    db_user: user_model.User,
    user_sch: user_schema.UserUpdate,
) -> user_model.User:
    """
    Method to update user details in the database.

    Args:
    -----
        session (Session): The current database session.
        db_user (user_model.User): The user model to update.
        user_sch (UserUpdate): The user schema to update.

    Returns:
    -------
        User: The updated user object.

    Raises:
    -------
        None
    """

    user_data = user_sch.model_dump(exclude_unset=True)
    
    # Use update=user_data for compatibility with both model_update and sqlmodel_update if needed
    db_user.sqlmodel_update(user_data, update=user_data) 

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user



async def search_users(
    session: Session,
    query: str,
    offset: int = 0,
    limit: int = 100,
) -> list[user_model.User]:
    """
    Search users by email, phone number, or full name.

    Args:
    -----
        session: The database session.
        query: Search term (email, phone_number, or name).
        offset: Records to skip.
        limit: Max records to return.
    Returns:
    --------
        list[user_model.User]: Matching user records.
    """
    # Prepare the query string for 'like' matching (case-insensitive for names/emails)
    q = f"%{query}%"

    # Start with the base statement for filtering by active status
    statement = select(user_model.User).where(user_model.User.active == True)


    # 2. Apply search criteria across multiple fields
    statement = statement.where(
        (user_model.User.email.ilike(q)) |
        (user_model.User.phone_number.like(q)) |
        (user_model.User.first_name.ilike(q)) |
        (user_model.User.last_name.ilike(q)) |
        # Search for full name (FirstName + ' ' + LastName)
        ((user_model.User.first_name + " " + user_model.User.last_name).ilike(q))
    )

    # 3. Apply pagination and ordering
    statement = (
        statement
        .offset(offset)
        .limit(limit)
        .order_by(user_model.User.id.desc())
    )

    # Execute the statement and return all results
    return session.exec(statement).all()
