from typing import List, Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api_v1.constants import PERSON_NOT_FOUND, FILM_NOT_FOUND
from api_v1.models import FilmShort, Person
from services.film import FilmService, get_film_service
from services.person import PersonService, get_person_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/{person_id:uuid}', response_model=Person)
async def person_details(person_id: UUID,
                         person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(str(person_id))
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PERSON_NOT_FOUND)

    return Person.from_db_model(person)


@router.get('/', response_model=List[Person])
async def person_search(
        query: Optional[str] = Query(""),
        sort: Optional[str] = Query(None, regex='^-?[a-zA-Z_]+$'),
        page_number: int = Query(1, alias='page[number]'),
        page_size: int = Query(50, alias='page[size]'),
        person_service: PersonService = Depends(get_person_service)) -> List[Person]:
    persons = await person_service.search(
        search_query=query,
        sort=sort,
        page_size=page_size, page_number=page_number)
    if not persons:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=PERSON_NOT_FOUND)

    return [Person(uuid=person.id, full_name=person.full_name, roles=person.roles, film_ids=person.film_ids)
            for person in persons]


@router.get('/{person_id:uuid}/film', response_model=List[FilmShort])
async def person_films(
        person_id: UUID,
        person_service: PersonService = Depends(get_person_service),
        film_service: FilmService = Depends(get_film_service)) -> List[FilmShort]:
    person = await person_service.get_by_id(str(person_id))
    person_films = await film_service.get_list(person.film_ids)
    if not person_films:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FILM_NOT_FOUND)

    return [FilmShort(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in person_films]
