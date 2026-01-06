"""
Utilities file for the API.
This file will contain utility functions that are used across the API.

Classes
-------
    None

Functions
-------
    validate_phone_number(phone: str)
        Validate a phone number and return it in the correct format.
    validate_id_number(id_number: str)
        Validate a partner's identification number.

Imports
-------
    settings
"""
from datetime import date

import phonenumbers

from fastapi import HTTPException, status
from phonenumbers.phonenumberutil import NumberParseException

from app.core.logging_config import app_logger


async def validate_phone_number(phone: str):
    """
    Method to validate a phone number

    Parameters
    ----------
        phone: str
            the phone number to be validated

    Returns
    -------
        phone: str
            if the phone number is valid (254) format

    Raises
    ------
        NumberParseException: if the phone number is not valid
        Exception: if any other error occurs
    """
    try:
        # Remove spaces, dashes, and trim
        clean_phone = phone.replace(" ", "").replace("-", "").strip()

        # Reject local format (starting with 0)
        if clean_phone.startswith("0"):
            raise NumberParseException(
                error_type=4,
                msg="Please use the +XXX or XXX format for phone number."
            )

        # Ensure phone has a + if it starts with 25
        phone_number = clean_phone
        if clean_phone.startswith("25"):
            phone_number = f"+{clean_phone}"

        # Parse & validate using phonenumbers
        user_phone = phonenumbers.parse(phone_number)
        if not phonenumbers.is_valid_number(user_phone):
            app_logger.warning(msg=f"Invalid phone number: {clean_phone}")
            raise NumberParseException(
                error_type=4,
                msg="Invalid phone number."
            )

        # Remove the '+' before returning (store only digits)
        normalized = phone_number[1:]

        # Enforce correct length
        if len(normalized) != 12:  # 254 + 9 digits
            app_logger.warning(msg=f"Invalid phone number length: {normalized}")
            raise NumberParseException(
                error_type=4,
                msg="Invalid phone number length."
            )

        return normalized

    except HTTPException as e:
        raise HTTPException(detail=e.detail, status_code=e.status_code)
    except NumberParseException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e._msg
        )
    except Exception as e:
        app_logger.error(f"Phone validation error: {str(e)}", exc_info=True)
        raise Exception("An error occurred while validating the phone number")


async def validate_id_number(id_number: str, nationality: str = 'KE'):
    """
    Method to validate partner identification number

    Parameters
    ----------
        id_number: str
            the identification number to be validated

    Returns
    -------
        id_number: str
            the accepted identification number

    Raises
    ------
        HTTPException: if the id_number is not correct or exists
    """
    try:
        if not id_number:
            return False

        clean_id_number = id_number.replace(' ', '').strip()

        if not clean_id_number:
            return False

        # 1. Check valid Kenya ID Number
        if nationality == 'KE':
            if len(clean_id_number) < 7 or len(clean_id_number) > 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='ID Number should be between 7 and 8 characters')

        return clean_id_number

    except HTTPException as e:
        raise HTTPException(
            detail=e.detail,
            status_code=e.status_code,
        )
    except Exception as e:
        print(e)
        raise Exception('An error occurred while validating the ID Number')


async def validate_age(dob: date):
    """
    Method to calculate age from a birth date

    Args:
    -----
        dob: date
            The date to calculate age from

    Returns
    -------
        dict: dict
            {'dob': dob, 'age': age}

    Raises
    ------
        None
    """
    try:
        if not dob:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Date of birth is required')

        today = date.today()
        age = today.year - dob.year - (
            (today.month, today.day) < (dob.month, dob.day))

        if age < 18:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Age must be above 18')

        return {'dob': dob, 'age': age}
    except HTTPException as e:
        raise HTTPException(
            detail=e.detail,
            status_code=e.status_code,
        )
    except Exception as e:
        print(e)
        app_logger.error(f'An error occurred while validating partner age: {e}')
        raise Exception('An error occurred while validating partner age')
