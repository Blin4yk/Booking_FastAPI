from datetime import datetime
from app.bookings.models import Bookings
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.hotels.schemas import SHotels
from app.service.base import BaseService
from sqlalchemy import Integer, and_, cast, func, insert, or_, select, cte
from app.database import async_session_maker, engine
from fastapi.encoders import jsonable_encoder

class HotelService(BaseService):
    model = Hotels

    @classmethod
    async def get_hotels(
        cls,
        location: str,
        date_from: datetime,
        date_to: datetime,
    ):
        async with async_session_maker() as session:
            booked_rooms = select(Bookings).where(
                or_(
                    and_(
                        Bookings.date_from >= date_from,
                        Bookings.date_from < date_to
                    ),
                    and_(
                        Bookings.date_from <= date_from,
                        Bookings.date_to > date_from
                    ),
                )
            ).cte("booked_rooms")
            
            count_rooms = select(
                Rooms.hotel_id,
                cast(Rooms.quantity - func.count(booked_rooms.c.id), Integer).label("rooms_left")
            ).select_from(Rooms).join(
                booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True
            ).group_by(
                Rooms.hotel_id, Rooms.quantity
            ).cte("count_rooms")

            hotels_location_rooms = select(
                Hotels,
                count_rooms.c.rooms_left
            ).select_from(Hotels).join(
                count_rooms, count_rooms.c.hotel_id == Hotels.id
            ).where(
                and_(
                    Hotels.location.like(f"%{location}%"),
                    count_rooms.c.rooms_left >= 1
                )
            )

            result = await session.execute(hotels_location_rooms)
            hotels = result.fetchall()

            return [
                SHotels.model_validate({**hotel[0].__dict__, "rooms_left": hotel[1]})
                for hotel in hotels
            ]
        
    @classmethod
    async def get_hotel_info(
        cls,
        hotel_id: int
    ):
        async with async_session_maker() as session:
            hotel = select(Hotels).where(
                Hotels.id == hotel_id
            )

            result = await session.execute(hotel)
            get_hotel = result.scalar()
            return get_hotel