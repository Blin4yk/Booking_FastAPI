from fastapi import APIRouter
from sqlalchemy import select

from app.bookings.models import Bookings
from app.bookings.schemas import SBooking
from app.bookings.service import BookingService
from app.database import async_session_maker
from app.rooms.models import Rooms

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)

@router.get("")
async def get_bookings() -> list[SBooking]:
    return await BookingService.find_all()


# FastAPI делает все за нас и пытается все ответы вывести в JSON формате
# SQLModel