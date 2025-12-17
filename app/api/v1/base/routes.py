from fastapi import APIRouter

router = APIRouter()

@router.get("/status", tags=["Status"])
async def api_status():
    """Basic health check/status endpoint."""
    return {"status": "ok", "version": "v1", "service": "AkibaFlow"}
