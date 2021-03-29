from enum import Enum
from typing import List, Optional, TypedDict

from pydantic.types import UUID4

from fastapi import Query

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
    description: Optional[str]
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

# remove magic number 1, 50
class Page:
    def __init__(
        self,
        page_size:  int = Query(50, alias='page[size]', ge=1),
        page_number: int = Query(1, alias='page[number]', ge=1)
    ) -> None:
        self.page_size = page_size
        self.page_number = page_number


class FilmSortEnum(str, Enum):
    imdb_rating_asc: str = 'imdb_rating:asc'
    imdb_rating_asc_alias: str = 'imdb_rating'
    imdb_rating_desc: str = 'imdb_rating:desc'
    imdb_rating_desc_alias: str = '-imdb_rating'


class FilmSort:
    def __init__(
        self,
        sort: FilmSortEnum = Query(
            FilmSortEnum.imdb_rating_desc_alias,
            title='Sort field',
            description='Sort field (default: "-imdb_rating", sort by imdb_rating in descending order)'
        ) 
    ) -> None:
        if sort == FilmSortEnum.imdb_rating_asc_alias:
            sort = FilmSortEnum.imdb_rating_asc
        if sort == FilmSortEnum.imdb_rating_desc_alias:
            sort = FilmSortEnum.imdb_rating_desc
        self.sort = sort
