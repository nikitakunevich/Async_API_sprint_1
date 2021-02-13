from http import HTTPStatus
from typing import List, Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from services.film import FilmService, get_film_service
import models.film

logger = logging.getLogger(__name__)
router = APIRouter()


class FilmShort(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float]


class Genre(BaseModel):
    uuid: str
    name: str


class PersonShort(BaseModel):
    uuid: str
    full_name: str


class FilmDetails(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: List[Genre]
    actors: List[PersonShort]
    writers: List[PersonShort]
    directors: List[PersonShort]

    @classmethod
    def from_film(cls, film: models.film.Film):
        return cls(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
            description=film.description,
            genre=[Genre(uuid=genre.id, name=genre.name) for genre in film.genres],
            actors=[PersonShort(uuid=person.id, full_name=person.name) for person in film.actors],
            writers=[PersonShort(uuid=person.id, full_name=person.name) for person in film.writers],
            directors=[PersonShort(uuid=person.id, full_name=person.name) for person in film.directors]

        )


@router.get('/{film_id:uuid}', response_model=FilmDetails)
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service)) -> FilmDetails:
    film = await film_service.get_by_id(str(film_id))
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return FilmDetails.from_film(film)


@router.get('/', response_model=List[FilmShort])
async def film_search(
        query: Optional[str] = Query(""),
        filter_genre: Optional[UUID] = Query(None, alias='filter[genre]'),
        sort: Optional[str] = Query(None, regex='^-?[a-zA-Z_]+$'),
        page_number: int = Query(1, alias='page[number]'),
        page_size: int = Query(50, alias='page[size]'),

        film_service: FilmService = Depends(get_film_service)) -> List[FilmShort]:
    films = await film_service.search(
        search_query=query,
        sort=sort,
        filter_genre=str(filter_genre) if filter_genre else None, page_size=page_size, page_number=page_number)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return [FilmShort(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]
