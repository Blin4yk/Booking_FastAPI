from fastapi import APIRouter

router = APIRouter(
    prefix="/hotels",
    tags=["Отели"]
)

@router.get("")
def get_hotels():
    pass