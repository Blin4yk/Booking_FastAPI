from sqlalchemy import select
from app.bookings.models import Bookings
from app.database import async_session_maker
from app.rooms.models import Rooms
from app.service.base import BaseService

#scalars().all() вызывается один раз

class BookingService(BaseService):
    model = Bookings