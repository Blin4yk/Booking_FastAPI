from typing import Optional
from pydantic import BaseModel
from sqlalchemy import BigInteger

class SHotels(BaseModel):
    id: int
    name: str
    location: str
    services: Optional[list[str]]
    rooms_quantity: int
    image_id: Optional[int]
    rooms_left: Optional[int] = None

    model_config = {
        "from_attributes": True
    }