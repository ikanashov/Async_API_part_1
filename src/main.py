import logging

import aioredis
import uvicorn as uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import film
from core.config import config
from core.logger import LOGGING
from db import elastic
from db import redis


app = FastAPI(
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=config.PROJECT_NAME,
    # Адрес документации в красивом интерфейсе
    docs_url='/api/openapi',
    # Адрес документации в формате OpenAPI
    openapi_url='/api/openapi.json',
    # Можно сразу сделать небольшую оптимизацию сервиса 
        # и заменить стандартный JSON-сереализатор на более шуструю версию, написанную на Rust
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    redis.redis = await aioredis.create_redis_pool(
        (config.REDIS_HOST, config.REDIS_PORT), 
        password=config.REDIS_PASSWORD, 
        minsize=10, maxsize=20
    )
    elastic.es = AsyncElasticsearch(
        hosts=[f'{config.ELASTIC_HOST}:{config.ELASTIC_PORT}'], 
        scheme=config.ELASTIC_SCHEME, 
        http_auth=(config.ELASTIC_USER, config.ELASTIC_PASSWORD)
    )


@app.on_event('shutdown')
async def shutdown():
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()


# Фильм на пробу из базы существующих 58bff82e-d892-4799-b9b3-964e9fb26398
# Подключаем роутер к серверу, указав префикс /v1/film
# Теги указываем для удобства навигации по документации
app.include_router(film.router, prefix='/v1/film', tags=['film'])


if __name__ == '__main__':
    # Приложение должно запускаться с помощью команды
    # `uvicorn main:app --host 0.0.0.0 --port 8000`
    # Но таким способом проблематично запускать сервис в дебагере,
        # поэтому сервер приложения для отладки запускаем здесь
    uvicorn.run(
        'main:app',
        host=config.UVICORN_HOST,
        port=config.UVICORN_PORT,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )