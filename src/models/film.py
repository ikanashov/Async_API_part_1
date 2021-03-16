from core.orjson import BaseModelOrjson


class Film(BaseModelOrjson):
    id: str
    imdb_rating: float
    title: str
    description: str

