
from datetime import date
from typing import List, Optional

from pydantic import Field

from core.orjson import BaseModelOrjson


class SFilmGenre(BaseModelOrjson):
    id: str = Field(..., alias='uuid')
    name: str
    description: str

    class Config:
        allow_population_by_field_name = True


class SFilmPerson(BaseModelOrjson):
    id: str = Field(..., alias='uuid')
    name: str = Field(..., alias='full_name')
    birth_date: Optional[date]
    death_date: Optional[date]

    class Config:
        allow_population_by_field_name = True


class SFilm(BaseModelOrjson):
    id: str = Field(..., alias='uuid')
    imdb_rating: float
    imdb_tconst: str
    filmtype: str
    genre: List[str]
    title: str
    description: Optional[str]
    directors_names: Optional[List[str]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    directors: Optional[List[SFilmPerson]]
    actors: Optional[List[SFilmPerson]]
    writers: Optional[List[SFilmPerson]]

    class Config:
        allow_population_by_field_name = True
