from fastapi import FastAPI
from app.api.v1 import router as api_router
from app.core.config import settings

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_V1_STR,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Include the main API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["health"])
async def root():
    """Basic health check endpoint."""
    return {"message": "AkibaFlow API is running! Access docs at /api/v1/docs"}
