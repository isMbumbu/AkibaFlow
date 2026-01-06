from datetime import datetime
from zoneinfo import ZoneInfo

from sqlmodel import Session, create_engine, select, SQLModel

from app.core.config import settings
from app.core.logging_config import app_logger


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


async def init_db(session: Session) -> None:
    """Initialize the database with the first superuser."""
    app_logger.warning(msg='Attempting to create initial user')

    # Import here to avoid circular imports
    from app.api.v1.user import (
        models as user_model,
        schemas as user_schema,
        repository as user_repository,
    )

    user = session.exec(
        select(user_model.User).where(
            user_model.User.email == settings.FIRST_SUPERUSER_EMAIL)
    ).first()

    if not user:
        app_logger.info(
            msg=f'Creating first superuser with email: {settings.FIRST_SUPERUSER_EMAIL}')

        now = datetime.now(tz=ZoneInfo(settings.APP_TIMEZONE))

        user_in = user_schema.UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            first_name='Base',
            last_name='User',
            active=True,
            created_at=now,
            updated_at=now,
        )

        user = await user_repository.create_user(
            session=session, user_create=user_in)


def get_session():
    with Session(engine) as session:
        yield session