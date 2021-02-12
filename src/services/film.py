import asyncio
import logging
from functools import cache
from typing import Optional, List, TypeVar, Callable

import elasticsearch.exceptions
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search, Q
from fastapi import Depends
from db.cache import ModelCache

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film

logger = logging.getLogger(__name__)
FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, cache: ModelCache, elastic: AsyncElasticsearch):
        self.cache = cache
        self.elastic = elastic

    async def search(self, search_query: str = "",
                     filter_genre: Optional[str] = None,
                     sort: Optional[str] = None,
                     page_number: int = 1,
                     page_size: int = 50) -> List[Film]:

        s = Search(using=self.elastic, index='movies')
        if search_query:
            multi_match_fields = ["title^4", "description^3", "genres_names^2", "actors_names^4", "writers_names",
                                  "directors_names^3"]
            s = s.query('multi_match', query=search_query, fields=multi_match_fields)
        if filter_genre:
            s = s.query('nested', path='genres', query=Q('bool', filter=Q('term', genres__id=filter_genre)))
        if sort:
            s = s.sort(sort)
        start = (page_number - 1) * page_size
        query = s[start: start + page_size].to_dict()
        films = await self.cache.get_by_elastic_query(query)  # Поиск в кэше
        if not films:
            results = await self.elastic.search(index='movies', body=query)
            films = [Film(**hit['_source']) for hit in results['hits']['hits']]
            await self.cache.set_by_elastic_query(query, films)
        return films

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self.cache.get_by_id(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            logger.debug('got film from elastic: %r', film)
            if not film:
                return None
            await self.cache.set_by_id(film_id, film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get('movies', film_id)
        except elasticsearch.exceptions.NotFoundError:
            return None
        return Film(**doc['_source'])


@cache
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(ModelCache(redis, Film, FILM_CACHE_EXPIRE_IN_SECONDS), elastic)


T = TypeVar('T')


async def run_in_executor(func: Callable[..., T], *args) -> T:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, func, *args)
