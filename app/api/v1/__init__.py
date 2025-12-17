from fastapi import APIRouter
from .base.routes import router as base_router
from .auth.routes import router as auth_router
from .user.routes import router as user_router

# The main router for /api/v1
router = APIRouter()

# Include sub-routers for each module
router.include_router(base_router, tags=["Status & Health"])
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(user_router, prefix="/user", tags=["User Management"])

# TODO: Add other routers here as you build them:
# router.include_router(transaction_router, prefix="/transactions", tags=["Transactions"])
# router.include_router(budget_router, prefix="/budgets", tags=["Budgets"])
