from posixpath import abspath, dirname
import sys
from typing import AsyncIterator

import aio_pika
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

import uvicorn

from app.config import settings

sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))

from app.bookings.router import router as router_bookings
from app.users.router import router as router_users
from app.hotels.router import router as router_hotels
from app.hotels.rooms.router import router as router_rooms


from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis

from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Инициализация Redis для кэширования
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
                              encoding="utf8",
                              decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")

    # Инициализация RabbitMQ
    rabbit_conn = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    app.state.rabbit_connection = rabbit_conn

    # Создание канала и очереди
    channel = await rabbit_conn.channel()
    await channel.declare_queue("user_login_queue", durable=True)
    app.state.rabbit_channel = channel

    yield

    # Закрытие соединения при завершении
    await rabbit_conn.close()

app = FastAPI(lifespan=lifespan)

app.include_router(router_users)
app.include_router(router_bookings)
app.include_router(router_hotels)
app.include_router(router_rooms)

# @app.on_event("startup")
# def startup():
#     redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="cache")


# Подключение эндпоинта для отображения метрик для их дальнейшего сбора Прометеусом
instrumentator = Instrumentator(
    should_group_status_codes=False,
    excluded_handlers=[".*admin.*", "/metrics"],
)
instrumentator.instrument(app).expose(app)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

