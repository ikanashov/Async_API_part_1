from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.models import FilmDetail, FilmShort, FilmSort

from services.film import FilmService, get_film_service


# Объект router, в котором регистрируем обработчики
router = APIRouter()


@router.get('/test', response_model=List[FilmShort])
async def get_all_film(
    sort: FilmSort = Query(
        FilmSort.imdb_rating_desc_alias,
        title='Sort field',
        description='Sort field (default: "-imdb_rating", sort by imdb_rating in descending order)'
        ),
    # I want to be like this page: DictPage = Query(...), but seems it doesn't alowed by pydantic and fastapi
    # I want use dict like page[number], page[size] as query parameters
    # https://github.com/tiangolo/fastapi/issues/884
    # https://github.com/tiangolo/fastapi/issues/1415
    # remove magic number 1, 50
    page_size:  int = Query(50, alias='page[size]', ge = 1),
    page_number: int = Query(1, alias='page[number]', ge = 1),    
    film_service: FilmService = Depends(get_film_service)
    ):
    if sort == FilmSort.imdb_rating_asc_alias:
        sort = FilmSort.imdb_rating_asc
    if sort == FilmSort.imdb_rating_desc_alias:
        sort = FilmSort.imdb_rating_desc
    films = await film_service._get_all_film_from_elastic(sort, page_size , page_number)
    films = [FilmShort(**film.dict(by_alias=True)) for film in films]
    return films

# Внедряем FilmService с помощью Depends(get_film_service)
@router.get('/{film_id}', response_model=FilmDetail)
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmDetail:
    film = await film_service.get_by_id(film_id)
    if not film:
        # Если фильм не найден, отдаём 404 статус
        # Желательно пользоваться уже определёнными HTTP-статусами, которые содержат enum
        # Такой код будет более поддерживаемым
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
        # Перекладываем данные из models.Film в Film
        # Обратите внимание, что у модели бизнес-логики есть поле description
        # Которое отсутствует в модели ответа API.
        # Если бы использовалась общая модель для бизнес-логики и формирования ответов API
        # вы бы предоставляли клиентам данные, которые им не нужны
        # и, возможно, данные, которые опасно возвращать
    return FilmDetail(**film.dict(by_alias=True))
