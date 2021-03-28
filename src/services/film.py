import logging
import logging.config
from functools import lru_cache
from typing import List, Optional

from aioredis import Redis

from elasticsearch import AsyncElasticsearch

from fastapi import Depends

from core.config import config
from core.logger import LOGGING

from db.elastic import get_elastic
from db.redis import get_redis

from models.film import SFilm

# need to remove magic number
FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('root')
logger.debug('Start logging')


# FilmService содержит бизнес-логику по работе с фильмами.
# Никакой магии тут нет. Обычный класс с обычными методами.
# Этот класс ничего не знает про DI — максимально сильный и независимый.
class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    async def get_by_id(self, film_id: str) -> Optional[SFilm]:
        # Пытаемся получить данные из кеша, потому что оно работает быстрее
        film = await self._film_from_cache(film_id)
        if not film:
            # Если фильма нет в кеше, то ищем его в Elasticsearch
            film = await self._get_film_from_elastic(film_id)
            if not film:
                # Если он отсутствует в Elasticsearch, значит, фильма вообще нет в базе
                return None
            # Сохраняем фильм  в кеш
            await self._put_film_to_cache(film)
        return film

    # Здесь же будем пытаться кэшировать и брать из кэша
    async def get_all_film(self, sort: str, page_size: int, page_number: int) -> Optional[List[SFilm]]:
        film = await self._get_all_film_from_elastic(sort, page_size, page_number)
        return film

    async def _get_all_film_from_elastic(self, sort: str, page_size: int, page_number: int) -> Optional[List[SFilm]]:
        from_ = page_size * (page_number - 1)
        # Подумать а стоит ли проверять на наличие правильного индекса, если индекс пустой то все работает
        # а вот если не существует то ошибка 404 надо ли ее обрабатывать ? подумать
        docs = await self.elastic.search(index=config.ELASTIC_INDEX, sort=sort, size=page_size, from_=from_)
        films = [SFilm(**doc['_source']) for doc in docs['hits']['hits']]
        # logger.debug(films)
        return films

    async def _get_film_from_elastic(self, film_id: str) -> Optional[SFilm]:
        doc = await self.elastic.get('movies', film_id)
        return SFilm(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[SFilm]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get
        data = await self.redis.get(film_id)
        if not data:
            return None

        # pydantic предоставляет удобное API для создания объекта моделей из json
        film = SFilm.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: SFilm):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS)


# get_film_service — это провайдер FilmService.
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Для их получения вы ранее создали функции-провайдеры в модуле db
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
