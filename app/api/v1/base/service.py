from fastapi import status, HTTPException

from app.api.deps import SessionDep
from app.core.logging_config import app_logger
from app.api.v1.user import repository as user_repository


async def liveness_check(session: SessionDep):
    """
    Implement liveness check by calling the db via user table

    Args
    ----
        session: The database session to use.

    Returns
    -------
        bool: True if ready
        Exception for any other error

    Raises:
    -------
        Exception: If there is an error during connection.
    """
    try:
        await user_repository.get_all_users(
            session=session, limit=200, offset=100)

        return {'detail': 'Welcome'}
    except Exception as e:
        session.rollback()
        app_logger.error(
            msg=f'Readiness check failed with error: {e}')
        raise HTTPException(
            detail='We experienced a technical issue. Please try again later.',
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
