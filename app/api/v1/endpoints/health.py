from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import MessageResponse

router = APIRouter()


@router.get("/health", response_model=MessageResponse)
async def health_check() -> MessageResponse:
    settings = get_settings()
    return MessageResponse(message=f"{settings.app_name} is running")
