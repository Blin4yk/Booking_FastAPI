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
from app.hotels.router import router as router_hotels
from app.hotels.rooms.router import router as router_rooms


app = FastAPI()

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_rooms)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

