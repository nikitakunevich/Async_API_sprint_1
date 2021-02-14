import logging

import elasticsearch.exceptions
from db.cache import ModelCache
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl.search import Search

logger = logging.getLogger(__name__)


class BaseESService:
    model = None
    index = None

    def __init__(self, cache: ModelCache, elastic: AsyncElasticsearch):
        self.cache = cache
        self.elastic = elastic

        if not self.model or not self.index:
            raise ValueError('Must set model and index value')

    async def search(self):
        raise NotImplementedError

    async def get_by_id(self, instance_id: str, index: str):
        instance = await self.cache.get_by_id(instance_id)
        if not instance:
            instance = await self._get_from_elastic(instance_id, index)
            logger.debug(f'got {instance.__class__.__name__} from elastic: {instance}')
            if not instance:
                return None
            await self.cache.set_by_id(instance_id, instance)
        return instance

    async def _get_from_elastic(self, instance_id: str, index: str):
        try:
            doc = await self.elastic.get(index, instance_id)
        except elasticsearch.exceptions.NotFoundError:
            return None
        return self.model(**doc['_source'])

    @staticmethod
    def _get_paginated_query(search: Search, page_number: int, page_size: int) -> dict:
        start = (page_number - 1) * page_size
        return search[start: start + page_size].to_dict()
