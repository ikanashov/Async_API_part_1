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

@router.get('/{person_id}', response_model=FilmPersonDetail)
async def person_details(person_id: str, film_service: FilmService = Depends(get_film_service)) -> FilmPersonDetail:
    person = await film_service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return FilmPersonDetail(**person.dict(by_alias=True))
