from fastapi import APIRouter, Depends, status, Query

from app.api import deps as global_deps
from app.api.v1.user import (
        schemas as user_schemas, service as user_service)


router = APIRouter(prefix='/user', tags=['User'])


@router.get(path='',
    status_code=status.HTTP_200_OK,
    response_model=list[user_schemas.UserRead])
async def get_all_users(
    session: global_deps.SessionDep,
    _: global_deps.CurrentUserDep, 
    offset: int = 0,
    limit: int = 100,
):
    """ Retrieve users (Active only) """
    return await user_service.get_all_users(
            session=session, offset=offset, limit=limit)


@router.get(path='/search',
    status_code=status.HTTP_200_OK,
    response_model=list[user_schemas.UserRead])
async def search_users(
    session: global_deps.SessionDep,
    _: global_deps.CurrentUserDep,
    query: str = Query(..., description="Search term for name, email, or phone number."),
    offset: int = 0,
    limit: int = 100,
):
    """ Search users by name, email, or phone number """
    return await user_service.search_users(
        session=session,
        query=query,
        offset=offset,
        limit=limit,
    )


@router.get(path='/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=user_schemas.UserRead)
async def get_user_by_id(
    user_id: int,
    session: global_deps.SessionDep,
    _: global_deps.CurrentUserDep): 
    """ Retrieve user by ID """
    return await user_service.get_user_by_id(
                session=session, user_id=user_id)


@router.post(path='',
    response_model=user_schemas.UserRead,
    status_code=status.HTTP_201_CREATED)
async def create_user(
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep,
    user_sch: user_schemas.UserCreate,
):
    """Create a new user"""
    return await user_service.create_user(
        user_sch=user_sch,
        session=session,
        created_by=current_user.id,
    )


@router.put(path='/{user_id}',
    response_model=user_schemas.UserRead,
    status_code=status.HTTP_201_CREATED)
async def update_user(
    user_id: int,
    session: global_deps.SessionDep,
    current_user: global_deps.CurrentUserDep, # FIXED ALIAS
    user_sch: user_schemas.UserUpdateReq,
):
    """Update user details"""
    return await user_service.update_user(
        session=session,
        user_id=user_id,
        user_sch=user_sch,
        updated_by=current_user.id,
    )
