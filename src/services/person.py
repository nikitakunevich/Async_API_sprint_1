import logging
from functools import cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl import Search
from fastapi import Depends

from core.config import CACHE_TTL
from db.cache import ModelCache

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person
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
        start = (page_number - 1) * page_size
        query = s[start: start + page_size].to_dict()
        films = await self.cache.get_by_elastic_query(query)
        if not films:
            results = await self.elastic.search(index=self.index, body=query)
            persons = [Person(**hit['_source']) for hit in results['hits']['hits']]
            await self.cache.set_by_elastic_query(query, persons)
        return persons


@cache
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(ModelCache(redis, Person, CACHE_TTL), elastic)
