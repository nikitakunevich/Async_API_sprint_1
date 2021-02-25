from typing import List, Optional

from aioredis import Redis
from elasticsearch_dsl.search import Search
from fastapi import Depends

from config import CACHE_TTL
from db.cache import ESModelCache
from db.elastic import AsyncElasticsearch, get_elastic
from db.redis import get_redis
from db.models import Genre
from services.base import BaseESService


class GenreService(BaseESService):
    model = Genre
    index = 'genres'

    def __init__(self, cache: ESModelCache[Genre], elastic: AsyncElasticsearch):
        super().__init__(cache, elastic)

    async def search(
        self,
        search_query: str = "",
        sort: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 50
    ) -> List[Genre]:
        s = Search(using=self.elastic, index=self.index)
        if search_query:
            s.query('match', full_name=search_query)
        if sort:
            s.sort(sort)
        return await self._search(s, page_number, page_size)


def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(ESModelCache[Genre](redis, Genre, CACHE_TTL), elastic)
