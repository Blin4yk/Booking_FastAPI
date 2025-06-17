from datetime import datetime
from fastapi import APIRouter
from fastapi_cache.decorator import cache

from app.exceptions import HotelIsAbsent
from app.hotels.service import HotelService

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"]
)

@router.get("{location}")
@cache(expire=60)
async def get_hotels_by_location_and_time(
    location: str,
    date_from: datetime,
    date_to: datetime
):
    return await HotelService.get_hotels(location, date_from, date_to)

@router.get("/id/{hotel_id}")
@cache(expire=60)
async def get_ones_hotel_info(hotel_id: int):
    hotel = await HotelService.get_hotel_info(hotel_id)
    if not hotel:
        await HotelIsAbsent