import json
import logging
import logging.config
from functools import lru_cache
from typing import Dict, List, Optional

from aioredis import Redis

from elasticsearch import AsyncElasticsearch

from fastapi import Depends

from core.config import config
from core.logger import LOGGING

from db.elastic import get_elastic
from db.redis import get_redis

from models.elastic import ESFilterGenre, ESQuery
from models.film import SFilm, SFilmGenre, SFilmPersonDetail


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

    # !!! Здесь начинаем работать с ручкой (слово-то какое) film !!!
    # get_by_id возвращает объект фильма. Он опционален, так как фильм может отсутствовать в базе
    # Не забыть переименовать название
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
    async def get_all_film(
        self,
        sort: str,
        page_size: int, page_number: int,
        genre_filter: str
    ) -> Optional[List[SFilm]]:

        if genre_filter is not None:
            filter = ESFilterGenre()
            filter.query.term.genre.value = genre_filter
            genre_filter = filter.json()
            logger.debug(genre_filter)
        films = await self._get_films_from_elastic(page_size, page_number, sort, body=genre_filter)
        return films

    async def search_film(self, query: str, page_size: int, page_number: int) -> Optional[List[SFilm]]:
        query_body = ESQuery()
        query_body.query.multi_match.query = query
        films = await self._get_films_from_elastic(page_size, page_number, body=query_body.json(by_alias=True))
        return films

    async def _get_films_from_elastic(
        self,
        page_size: int, page_number: int,
        sort: str = None, body: str = None
    ) -> Optional[List[SFilm]]:

        from_ = page_size * (page_number - 1)
        # Подумать а стоит ли проверять на наличие правильного индекса, если индекс пустой то все работает
        # а вот если не существует то ошибка 404 надо ли ее обрабатывать ? подумать
        docs = await self.elastic.search(
            index=config.ELASTIC_INDEX,
            sort=sort,
            size=page_size,
            from_=from_,
            body=body
        )
        films = [SFilm(**doc['_source']) for doc in docs['hits']['hits']]
        # logger.debug(films)
        return films

    async def _get_film_from_elastic(self, film_id: str) -> Optional[SFilm]:
        doc = await self.elastic.get(config.ELASTIC_INDEX, film_id)
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
        await self.redis.set(film.id, film.json(), expire=config.CLIENTAPI_CACHE_EXPIRE)
    # !!! Здесь заканчиваем работать с ручкой (слово-то какое) film !!!

    # !!! Здесь начинаем работать с ручкой (слово-то какое) genre !!!
    async def get_all_genre(
        self,
        sort: str,
        page_size: int, page_number: int,
    ) -> Optional[List[SFilmGenre]]:

        genres = await self._get_genres_from_elastic(page_size, page_number, sort)
        return genres

    async def _get_genres_from_elastic(
        self,
        page_size: int, page_number: int,
        sort: str = None, body: str = '{"query": {"match_all": {}}}'
    ) -> Optional[List[SFilmGenre]]:

        from_ = page_size * (page_number - 1)
        # Подумать а стоит ли проверять на наличие правильного индекса, если индекс пустой то все работает
        # а вот если не существует то ошибка 404 надо ли ее обрабатывать ? подумать
        docs = await self.elastic.search(
            index=config.ELASTIC_GENRE_INDEX,
            sort=sort,
            size=page_size,
            from_=from_,
            body=body
        )
        genres = [SFilmGenre(**doc['_source']) for doc in docs['hits']['hits']]
        # logger.debug(genres)
        return genres

    async def get_genre_by_id(self, genre_id: str) -> Optional[SFilmGenre]:
        # Пытаемся пока не получать данные из кеша, потому что оно работает быстрее, но это следующее задание
        genre = await self._get_genre_from_elastic(genre_id)
        if not genre:
            # Если он отсутствует в Elasticsearch, значит, жанра вообще нет в базе
            return None
        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[SFilmGenre]:
        doc = await self.elastic.get(config.ELASTIC_GENRE_INDEX, genre_id)
        return SFilmGenre(**doc['_source'])
    # !!! Здесь заканчиваем работать с ручкой (слово-то какое) genre !!!

    # !!! Здесь начинаем работать с ручкой (слово-то какое) person !!!
    async def get_all_person(
        self,
        sort: str,
        page_size: int, page_number: int,
    ) -> Optional[List[SFilmPersonDetail]]:

        persons = await self._get_persons_from_elastic(page_size, page_number, sort)
        return persons

    async def search_person(self, query: str, page_size: int, page_number: int) -> Optional[List[SFilmPersonDetail]]:
        query_body: Dict = {'query': {'match': {'full_name': {'query': query, 'fuzziness': 'AUTO'}}}}
        persons = await self._get_persons_from_elastic(page_size, page_number, body=json.dumps(query_body))
        return persons

    async def _get_persons_from_elastic(
        self,
        page_size: int, page_number: int,
        sort: str = None, body: str = '{"query": {"match_all": {}}}'
    ) -> Optional[List[SFilmPersonDetail]]:

        from_ = page_size * (page_number - 1)
        # Подумать а стоит ли проверять на наличие правильного индекса, если индекс пустой то все работает
        # а вот если не существует то ошибка 404 надо ли ее обрабатывать ? подумать
        docs = await self.elastic.search(
            index=config.ELASTIC_PERSON_INDEX,
            sort=sort,
            size=page_size,
            from_=from_,
            body=body
        )
        persons = [SFilmPersonDetail(**doc['_source']) for doc in docs['hits']['hits']]
        # logger.debug(persons)
        return persons

    async def get_person_by_id(self, person_id: str) -> Optional[SFilmPersonDetail]:
        # Пытаемся пока не получать данные из кеша, потому что оно работает быстрее, но это следующее задание
        person = await self._get_person_from_elastic(person_id)
        if not person:
            # Если он отсутствует в Elasticsearch, значит, человека вообще нет в базе
            return None
        return person

    async def _get_person_from_elastic(self, person_id: str) -> Optional[SFilmPersonDetail]:
        doc = await self.elastic.get(config.ELASTIC_PERSON_INDEX, person_id)
        return SFilmPersonDetail(**doc['_source'])
    # !!! Здесь заканчиваем работать с ручкой (слово-то какое) person !!!


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
