from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from api.v1.models import FilmPersonDetail

from services.film import FilmService, get_film_service


# Объект router, в котором регистрируем обработчики
router = APIRouter()

@router.get('/person', response_model=List[FilmPersonDetail])
async def get_all_genre(
    film_service: FilmService = Depends(get_film_service)
) -> List[FilmPersonDetail]:
    return [FilmPersonDetail(
        uuid = '81bf1c0e-fa7c-423f-b6d5-c676dca68dc9',
        full_name = 'test',
        role = 'actor, director',
        film_ids = ['81bf1c0e-fa7c-423f-b6d5-c676dca68dc9','c5348b55-68b1-4273-8fbd-9c1372c16039']
        )]

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