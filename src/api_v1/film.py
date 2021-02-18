from typing import List, Optional
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api_v1.constants import FILM_NOT_FOUND
from api_v1.models import FilmShort, FilmDetails
from services.film import FilmService, get_film_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/{film_id:uuid}', response_model=FilmDetails)
async def film_details(film_id: UUID, film_service: FilmService = Depends(get_film_service)) -> FilmDetails:
    film = await film_service.get_by_id(str(film_id))
    if not film:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FILM_NOT_FOUND)

    return FilmDetails.from_db_model(film)


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=FILM_NOT_FOUND)

    return [FilmShort(uuid=film.id, title=film.title, imdb_rating=film.imdb_rating) for film in films]
