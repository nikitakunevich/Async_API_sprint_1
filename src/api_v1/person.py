from http import HTTPStatus
from typing import List, Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from api_v1.film import FilmShort
from models.person import Person
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service

logger = logging.getLogger(__name__)
router = APIRouter()


class PersonApiModel(BaseModel):
    uuid: str
    full_name: str
    roles: List[str]
    film_ids: List[str]

    @classmethod
    def from_person(cls, person: Person):
        return cls(
            uuid=person.id,
            full_name=person.full_name,
            roles=person.roles,
            film_ids=person.film_ids
        )


@router.get('/{person_id:uuid}', response_model=PersonApiModel)
async def person_details(person_id: UUID,
                         person_service: PersonService = Depends(get_person_service)) -> PersonApiModel:
    person = await person_service.get_by_id(str(person_id), 'persons')
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return PersonApiModel.from_person(person)


@router.get('/', response_model=List[PersonApiModel])
async def person_search(
        query: Optional[str] = Query(""),
        sort: Optional[str] = Query(None, regex='^-?[a-zA-Z_]+$'),
        page_number: int = Query(1, alias='page[number]'),
        page_size: int = Query(50, alias='page[size]'),
        person_service: PersonService = Depends(get_person_service)) -> List[PersonApiModel]:
    persons = await person_service.search(
        search_query=query,
        sort=sort,
        page_size=page_size, page_number=page_number)
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return [PersonApiModel(uuid=person.id, full_name=person.full_name, roles=person.roles, film_ids=person.film_ids)
            for person in persons]


@router.get('/{person_id:uuid}/film', response_model=List[FilmShort])
async def person_films(
        person_id: UUID,
        person_service: PersonService = Depends(get_person_service),
        film_service: FilmService = Depends(get_film_service)) -> List[FilmShort]:
    person = await person_service.get_by_id(str(person_id), 'persons')
    person_films = await film_service.get_list(person.film_ids)
    if not person_films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return [FilmShort(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in person_films]
