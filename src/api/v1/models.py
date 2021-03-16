from core.orjson import BaseModelOrjson

# Модель ответа API
class FilmDetail(BaseModelOrjson):
    id: str
    imdb_rating: float
    title: str