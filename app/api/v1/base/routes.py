from fastapi import APIRouter

from app.api import deps as global_deps
from app.core.logging_config import app_logger
from app.api.v1.base import service as base_service

router = APIRouter(prefix='', tags=['Home'])


@router.get('/')
async def home(session: global_deps.SessionDep) -> dict:
    app_logger.info('Home endpoint accessed')
    return await base_service.liveness_check(session=session)


@router.get('/liveness-check')
async def liveness_check(
    session: global_deps.SessionDep,) -> dict:
    """ Liveness check for the container """
    return await base_service.liveness_check(session=session)
