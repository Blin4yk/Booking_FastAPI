from datetime import datetime
from fastapi import APIRouter

from app.hotels.service import HotelService

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"]
)

@router.get("{location}")
async def get_hotels(
    location: str,
    date_from: datetime,
    date_to: datetime
):
    return await HotelService.get_hotels(
        location,
        date_from,
        date_to
    )