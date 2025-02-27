from posixpath import abspath, dirname
import sys
from fastapi import Depends, FastAPI, HTTPException, Query
import uvicorn
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))

from app.bookings.router import router as router_bookings
from app.users.router import router as router_users

app = FastAPI()

app.include_router(router_users)
app.include_router(router_bookings)

class BookingArgs:
    def __init__(self, 
        location: str,
        date_from: date,
        date_to: date,
        has_spa: Optional[bool] = None,
        starts: Optional[int] = Query(None, ge=1, le=5)
        ):
        self.location = location
        self.date_from = date_from
        self.date_to = date_to
        self.has_spa = has_spa
        self.starts = starts

@app.get("/hotels")
def get_hotels(
    bookingArgs: BookingArgs = Depends()
):
    return bookingArgs

class SBooking(BaseModel):
    room_id: int
    date_from: date
    date_to: date
    price: int


@app.post("/bookings")
def add_booking(booking: SBooking):
    pass

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

