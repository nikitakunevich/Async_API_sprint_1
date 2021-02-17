import asyncio
import logging
from functools import cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search, Q
from fastapi import Depends

from config import CACHE_TTL
from db.cache import ModelCache
from db.elastic import get_elastic
from db.models import Film
from db.redis import get_redis
from services.base import BaseESService

logger = logging.getLogger(__name__)


class FilmService(BaseESService):
    model = Film
    index = 'movies'

    async def search(self, search_query: str = "",
                     filter_genre: Optional[str] = None,
                     sort: Optional[str] = None,
                     page_number: int = 1,
                     page_size: int = 50) -> List[Film]:

        s = Search(using=self.elastic, index=self.index)
        if search_query:
            multi_match_fields = ["title^4", "description^3", "genres_names^2", "actors_names^4", "writers_names",
                                  "directors_names^3"]
            s = s.query('multi_match', query=search_query, fields=multi_match_fields)
        if filter_genre:
            s = s.query('nested', path='genres', query=Q('bool', filter=Q('term', genres__id=filter_genre)))
        if sort:
            s = s.sort(sort)
        return await self._search(s, page_number, page_size)

    async def get_list(self, film_ids: List[str]) -> List[Film]:
        # noinspection PyTypeChecker
        films: List[Optional[Film]] = await asyncio.gather(*[self.cache.get_by_id(film_id) for film_id in film_ids])

        films = [film for film in films if film is not None]
        film_id_mapping = {film.id: film for film in films}
        not_cached_ids = [film_id for film_id in film_ids if film_id not in film_id_mapping]

        not_cached_films: List[Film] = await self._get_list_from_elastic(not_cached_ids)
        if not_cached_films:
            await asyncio.gather(*[self.cache.set_by_id(film.id, film) for film in not_cached_films])
        films.extend(not_cached_films)
        if not films:
            return []

        return films


@cache
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(ModelCache[Film](redis, Film, CACHE_TTL), elastic)
