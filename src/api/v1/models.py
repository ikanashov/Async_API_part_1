from enum import Enum
from typing import List, Optional, TypedDict

from pydantic.types import UUID4

from core.orjson import BaseModelOrjson


class FilmGenre(BaseModelOrjson):
    uuid: UUID4
    name: str


class FilmPerson(BaseModelOrjson):
    uuid: UUID4
    full_name: str


# Модель ответа API
class FilmShort(BaseModelOrjson):
    uuid: UUID4
    title: str
    imdb_rating: float


class FilmDetail(FilmShort):
    description: Optional[str]
    genre: List[str]
    actors: Optional[List[FilmPerson]]
    writers: Optional[List[FilmPerson]]
    directors: Optional[List[FilmPerson]]


class PersonDetail(FilmPerson):
    role: str
    film_ids: List[UUID4]


# unused class remove it
class DictPage(TypedDict):
    size: int
    number: int


# unused class remove it
class Page(BaseModelOrjson):
    page: DictPage


class FilmSort(str, Enum):
    imdb_rating_asc: str = 'imdb_rating:asc'
    imdb_rating_asc_alias: str = 'imdb_rating'
    imdb_rating_desc: str = 'imdb_rating:desc'
    imdb_rating_desc_alias: str = '-imdb_rating'
