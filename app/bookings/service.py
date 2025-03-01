from datetime import date
from sqlalchemy import and_, func, insert, or_, select, cte
from app.bookings.models import Bookings
from app.database import async_session_maker, engine
from app.hotels.rooms.models import Rooms
from app.service.base import BaseService

#scalars().all() вызывается один раз

class BookingService(BaseService):
    model = Bookings

    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date
    ):
        async with async_session_maker() as session:
            booked_rooms = select(Bookings).where(
                and_(
                    Bookings.room_id == room_id,
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
                )
            ).cte("booked_rooms") # with
            get_rooms_left = select(
                (Rooms.quantity - func.count(booked_rooms.c.id)).label("rooms_left")
                ).select_from(Rooms).join(
                    booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True
                ).where(Rooms.id == room_id).group_by(
                    Rooms.quantity, booked_rooms.c.room_id
                )

            rooms_left = await session.execute(get_rooms_left)
            rooms_left: int = rooms_left.scalar()
            rooms_left = rooms_left if rooms_left is not None else 0

            if rooms_left > 0:
                get_price = select(Rooms.price).filter_by(id=room_id)
                price = await session.execute(get_price)
                price: int = price.scalar()
                add_booking = insert(Bookings).values(
                    room_id=room_id,
                    user_id=user_id,
                    date_from=date_from,
                    date_to=date_to,
                    price=price,
                ).returning(Bookings)

                new_booking = await session.execute(add_booking)
                await session.commit()
                return new_booking.scalar() # Так как передаем модель Bookings полностью, то мы можем использовать  scalar() для возвращения модели
            else:
                return None
        