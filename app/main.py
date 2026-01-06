import time

from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.logging_config import app_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for the FastAPI application."""
    app_logger.warning(msg=f'App re-started at {datetime.now()}')
    yield
    app_logger.warning(msg=f'App shutdown at {datetime.now()}')


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    docs_url=f'{settings.API_VERSION_STR}/docs',
    openapi_url=f'{settings.API_VERSION_STR}/openapi.json',
)


# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


# --- Request/Response Logging Middleware ---
@app.middleware('http')
async def log_requests(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        app_logger.info(
            f'Request: {request.method} {request.url.path} - '
            f'Status: {response.status_code} - '
            f'Process Time: {process_time:.4f}s'
        )
        return response
    except Exception as e:
        process_time = time.time() - start_time
        app_logger.exception(
            f'Error during request: {request.method} {request.url.path} - '
            f'Process Time: {process_time:.4f}s - '
            f'Exception: {e}'
        )
        raise # Re-raise the exception after logging it


@app.get(path='/', tags=['Default'])
async def home() -> dict:
    app_logger.info('Home endpoint accessed')
    return {'detail': 'Welcome'}


app.include_router(router=api_router, prefix=settings.API_VERSION_STR)
