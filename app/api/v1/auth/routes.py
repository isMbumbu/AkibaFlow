from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api import deps as global_deps
from app.api.v1.auth import (
    schemas as auth_schemas, service as auth_service)

from app.api.v1.user import schemas as user_schemas

router = APIRouter(prefix='/auth', tags=['Auth'])


@router.post('/login')
async def login(
    session: global_deps.SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> auth_schemas.Token:
    """
    Route to handle login for users.
    """
    return await auth_service.login(
        session=session, form_data=form_data)


@router.get(
    path='/whoami',
    status_code=status.HTTP_200_OK,
    response_model=auth_schemas.UserRead,
)
async def whoami(
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
):
    return await auth_service.whoami(
        session=session, current_user=current_user)


@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=auth_schemas.UserRead,
)
async def register( 
    session: global_deps.SessionDep, 
    user_in: user_schemas.UserRegister,
) -> auth_schemas.UserRead:
    """
    Route to register a new user. This endpoint is publicly accessible.
    """
    return await auth_service.register(
        session=session, user_in=user_in
    )
