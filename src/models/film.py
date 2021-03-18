from typing import List, Optional

from pydantic import Field

from core.orjson import BaseModelOrjson


class SFilmPerson(BaseModelOrjson):
    id: str = Field(..., alias='uuid')
    name: str

    class Config:
        allow_population_by_field_name = True


class Film(BaseModelOrjson):
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
