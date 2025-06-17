import datetime
import uuid
from urllib import request

from fastapi import APIRouter, Depends, Response, BackgroundTasks
from fastapi_cache.decorator import cache
from pydantic import json
import aio_pika
from app.exceptions import IncorrectEmailOrPassword, UserAlreadyExistsException
from app.users.auth import authenticate_user, create_access_token, get_password_hash
from app.users.dependencies import get_current_admin_user, get_current_user
from app.users.models import Users
from app.users.schemas import SUserAuth
from app.users.service import UsersService
router = APIRouter(
    prefix="/auth",
    tags=["Auth & Пользователи"]
)

@router.post("/register")
async def register_user(user_data: SUserAuth):
    exiting_user = await UsersService.find_one_or_none(email=user_data.email)
    if exiting_user:
        raise UserAlreadyExistsException
    hashed_password = get_password_hash(user_data.password)
    await UsersService.add(email=user_data.email, hashed_password=hashed_password)


async def send_login_event(user_id: str, email: str, rabbit_channel: aio_pika.abc.AbstractChannel):
    """Отправка события в RabbitMQ"""
    event_data = {
        "event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "email": email,
        "event_type": "user_login",
        "timestamp": datetime.utcnow().isoformat()
    }

    message = aio_pika.Message(
        body=json.dumps(event_data).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )

    await rabbit_channel.default_exchange.publish(
        message,
        routing_key="user_login_queue"
    )


@router.post("/login")
async def login_user(
        response: Response,
        user_data: SUserAuth,
        background_tasks: BackgroundTasks
):
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise IncorrectEmailOrPassword

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("booking_access_token", access_token, httponly=True)

    # Получаем RabbitMQ channel из состояния приложения
    rabbit_channel = request.app.state.rabbit_channel

    # Добавляем фоновую задачу
    background_tasks.add_task(
        send_login_event,
        user_id=str(user.id),
        email=user.email,
        rabbit_channel=rabbit_channel
    )

    return {"access_token": access_token}

@router.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("booking_access_token")


@router.get("/me")
@cache(expire=60)
async def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user

@router.get("/all")
@cache(expire=60)
async def read_users_all(current_user: Users = Depends(get_current_admin_user)):
    return await UsersService.find_all()
