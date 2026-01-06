import random
import asyncio

from datetime import datetime, timedelta

from sqlmodel import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logging_config import app_logger
from app.api import utils as global_utils, libs as global_libs
from app.core.security import verify_password, get_password_hash
from app.api.v1.user import (
    schemas as user_schema, repository as user_repository)


async def authenticate_with_email(
        session: Session, email: str, password: str):
    """
    Method to authenticate a user by email and password.

    Args:
    -----
        session (Session): The current database session.
        email (str): The email of the user.
        password (str): The password of the user.

    Returns:
    -------
        User | None: The authenticated user object if successful, otherwise None.

    Raises:
    -------
        None
    """
    try:
        app_logger.warning(
            msg=f'Attempting to login user with email - {email}')

        db_user = await user_repository.get_user_by_email(
            session=session, user_email=email)

        if not db_user:
            app_logger.warning(
                msg=f'Login failed for user with email - {email} - Email not found')
            return None

        password_verified = await verify_password(
            plain_password=password, hashed_password=db_user.hashed_password)

        if not password_verified:
            app_logger.warning(f"Failed login user '{email}' - Incorrect email or password")
            return None

        app_logger.info(f"Successfully authenticated user '{email}'")

        return db_user
    except Exception as e:
        app_logger.error(f"Failed to authenticate user '{email}' error: {e}")
        raise e


async def authenticate_with_phone(
        session: Session, phone: str, otp: str):
    """
    Method to authenticate a user by OTP.

    Args:
    -----
        session (Session): The current database session.
        phone (str): The phone number of the user.
        otp (str): The otp sent to the user.

    Returns:
    -------
        User | None: The authenticated user object if successful, otherwise None.

    Raises:
    -------
        None
    """
    try:
        app_logger.warning(
            msg=f'Attempting to login user with OTP - {phone}')

        # Validate phone number format
        phone = await global_utils.validate_phone_number(phone=phone)

        db_user = await user_repository.get_user_by_phone(
            session=session, user_phone=phone)

        if not db_user:
            app_logger.warning(
                msg=f'Login failed for user with phone - {phone} - Phone not found')
            return None

        password_verified = await verify_password(
            plain_password=otp, hashed_password=db_user.hashed_password)

        if not password_verified:
            app_logger.warning(
                msg=f"Failed login user '{phone}' - Incorrect OTP or password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='OTP provided has expired or is invalid',
            )

        app_logger.info(f"Successfully authenticated user with phone '{phone}'")

        return db_user
    except HTTPException as e:
        app_logger.error(msg=e.detail)
        raise HTTPException(
            detail=e.detail,
            status_code=e.status_code,
        )
    except Exception as e:
        app_logger.error(f"Failed to authenticate with OTP '{phone}' error: {e}")
        raise e


async def update_user_login_details(
        session: Session, db_user, action_type: str = 'login'):
    """
    Method to update user login details.
    """
    try:
        app_logger.info(
            msg=f"Updating login details for user '{db_user.email}'")

        now = datetime.now()

        user_sch = user_schema.UserLoginUpdate(
            last_login=now,
            hashed_password=db_user.hashed_password,
        )

        if action_type != 'login':

            hashed_password = await asyncio.to_thread(
                get_password_hash, action_type
            )

            user_sch.hashed_password = hashed_password

        app_logger.info(
            msg=f'User login details updated for {db_user.email}')

        return await asyncio.to_thread(
            user_repository.update_user_login_details, session, db_user, user_sch
        )

    except Exception as e:
        app_logger.error(f"Failed to update login details for user '{db_user.email}' error: {e}")
        raise e


# async def process_otp_request(session: Session, phone: str):
#     """
#     Method Process OTP request for a user.
#     """
#     try:
#         app_logger.info(f"Processing OTP request for '{phone}'")

#         # Validate phone number format
#         phone = await global_utils.validate_phone_number(phone=phone)


#         db_user = await asyncio.to_thread(
#             user_repository.get_user_by_phone, session, phone
#         )

#         if not db_user:
#             app_logger.warning(
#                 msg=f'OTP request failed - User with phone {phone} not found')
#             return False

#         # Check if OTP is still valid
#         is_valid_otp = False

#         if db_user.otp_last_issued_at:
#             is_valid_otp = await _verify_otp_validity(
#                 time_issued=db_user.otp_last_issued_at)

#         if is_valid_otp:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail='A valid OTP has already been sent. Please re-use it.',
#             )

#         # Generate a new OTP
#         otp = await _generate_otp()

#         # Check for superuser otp only to be used in staging
#         if phone == settings.FIRST_SUPERUSER_PHONE:
#             otp = settings.FIRST_SUPERUSER_OTP
#             app_logger.warning(
#                 msg=f'Superuser phone number detected - '
#                     f'OTP {otp}: will not be changed')

#         await global_libs.send_sms_at(
#             recipients=[f'+{phone}'],
#             message=f'Your OTP is {otp}',
#             premium=False,
#             login=True,
#         )
#         app_logger.info(
#             msg=f'OTP generated for user {phone} - OTP: {otp}')

#         # Update user login details with OTP
#         await update_user_login_details(
#             session=session,
#             db_user=db_user,
#             action_type=otp,
#         )

#         app_logger.info(
#             msg=f"OTP request processed successfully for phone '{phone}'")

#         return True
#     except HTTPException as e:
#         app_logger.error(f"Failed to process OTP request for phone '{phone}' error: {e.detail}")
#         raise HTTPException(
#             detail=e.detail,
#             status_code=e.status_code,
#         )
#     except Exception as e:
#         app_logger.error(f"Failed to process OTP request for phone '{phone}' error: {e}")
#         raise e


# async def _generate_otp():
#     """
#     A utility function to generate random passcodes
#     """
#     randomlist = []
#     for _ in range(0, 2):
#         n = random.randint(10, 99)
#         randomlist.append(str(n))

#     return str("".join(randomlist))


# async def _verify_otp_validity(time_issued: datetime):
#     """
#     Method to verify if an OTP is valid.
#     """
#     valid = False

#     now = datetime.now()
#     time_difference = now - time_issued
#     expiry_delta = timedelta(
#                 minutes=settings.OTP_EXPIRE_MINUTES)

#     app_logger.info(
#         msg=f'Checking OTP validity - Time issued: {time_issued}, '
#             f'Current time: {now}, OTP expiry delta: {expiry_delta} '
#             f'Time Difference: {time_difference}')

#     if time_difference < expiry_delta:
#         valid = True

#     return valid
