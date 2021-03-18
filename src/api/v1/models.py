from typing import Optional, List

from pydantic.types import UUID4
from core.orjson import BaseModelOrjson

class FilmGenre(BaseModelOrjson):
    uuid: UUID4
    name: str


class FilmPerson(BaseModelOrjson):
    uuid: UUID4
    name: str


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
