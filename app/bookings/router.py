from datetime import date
from fastapi import APIRouter, Depends, Request
from sqlalchemy import select

from app.bookings.models import Bookings
from app.bookings.schemas import SBooking
from app.bookings.service import BookingService
from app.database import async_session_maker
from app.exceptions import BookingCanNotDelete, RoomCanNotBeBooked
from app.hotels.rooms.models import Rooms
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.users.service import UsersService

router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)

@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)): #-> list[SBooking]:
    return await BookingService.find_all(user_id=user.id)


@router.post("")
async def add_booking(
    room_id: int, date_from: date, date_to: date,
    user: Users = Depends(get_current_user),
):
    booking = await BookingService.add(user.id, room_id, date_from, date_to)
    if not booking:
        raise RoomCanNotBeBooked
    
@router.delete("{booking_id}")
async def delete_booking(
    booking_id: int, 
    user: Users = Depends(get_current_user)
):
    delete_booking = await BookingService.delete(user.id,  booking_id)
    if not delete_booking:
        raise BookingCanNotDelete
# FastAPI делает все за нас и пытается все ответы вывести в JSON формате
# SQLModel