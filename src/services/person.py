import logging
from functools import cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search
from fastapi import Depends

from config import CACHE_TTL
from db.cache import ESModelCache
from db.elastic import get_elastic
from db.redis import get_redis
from db.models import Person
from services.base import BaseESService

logger = logging.getLogger(__name__)


class PersonService(BaseESService):
    model = Person
    index = 'persons'

    async def search(self, search_query: str = "",
                     filter_genre: Optional[str] = None,
                     sort: Optional[str] = None,
                     page_number: int = 1,
                     page_size: int = 50) -> List[Person]:

        s = Search(using=self.elastic, index=self.index)
        if search_query:
            s = s.query('match', full_name=search_query)
        if sort:
            s = s.sort(sort)
        return await self._search(s, page_number, page_size)


@cache
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(ESModelCache[Person](redis, Person, CACHE_TTL), elastic)
