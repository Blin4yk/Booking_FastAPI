from fastapi_cache.decorator import cache

from app.hotels.router import router

@router.get("/{hotel_id}/rooms")
@cache(expire=60)
def get_rooms():
    pass