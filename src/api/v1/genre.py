from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.v1.models import FilmGenre, FilmGenreSort, Page

from services.film import FilmService, get_film_service


# Объект router, в котором регистрируем обработчики
router = APIRouter()

@router.get('', response_model=List[FilmGenre])
async def get_all_genre(
    sort: FilmGenreSort = Depends(),
    page: Page = Depends(),
    film_service: FilmService = Depends(get_film_service)
) -> List[FilmGenre]:
    genres = await film_service.get_all_genre(sort.sort, page.page_size, page.page_number)
    genres = [FilmGenre(**film.dict(by_alias=True)) for film in genres]
    return genres

'''
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
'''