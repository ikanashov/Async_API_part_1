from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.v1.models import FilmPersonDetail, FilmPersonSort, Page

from services.film import FilmService, get_film_service


# Объект router, в котором регистрируем обработчики
router = APIRouter()

@router.get('', response_model=List[FilmPersonDetail])
async def get_all_person(
    sort: FilmPersonSort = Depends(),
    page: Page = Depends(),
    film_service: FilmService = Depends(get_film_service)
) -> List[FilmPersonDetail]:
    persons = await film_service.get_all_person(sort.sort, page.page_size, page.page_number)
    persons = [FilmPersonDetail(**person.dict(by_alias=True)) for person in persons]
    return persons

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