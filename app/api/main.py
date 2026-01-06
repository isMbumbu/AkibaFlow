from fastapi import APIRouter

from app.api.v1.base import routes as base_routes
from app.api.v1.auth import routes as auth_routes
from app.api.v1.user import routes as user_routes

api_router = APIRouter()

# Include all routers
api_router.include_router(router=base_routes.router)
api_router.include_router(router=auth_routes.router)
api_router.include_router(router=user_routes.router)
