import logging
from abc import ABC
from typing import List

import elasticsearch.exceptions
import elasticsearch.exceptions
from elasticsearch import AsyncElasticsearch
from elasticsearch_dsl.search import Search

from db.cache import ModelCache

logger = logging.getLogger(__name__)


class BaseESService(ABC):
    model = None
    index = None

    def __init__(self, cache: ModelCache, elastic: AsyncElasticsearch):
        self.cache = cache
        self.elastic = elastic

        if not self.model or not self.index:
            raise ValueError('Must set model and index value')

    async def search(self):
        raise NotImplementedError

    async def get_by_id(self, instance_id: str):
        instance = await self.cache.get_by_id(instance_id)
        if not instance:
            instance = await self._get_from_elastic(instance_id, self.index)
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

    async def _search(self, search: Search, page_number: int, page_size: int):
        query = self._get_paginated_query(search, page_number, page_size)
        items = await self.cache.get_by_elastic_query(query)
        if not items:
            search_result = await self.elastic.search(index=self.index, body=query)
            items = [self.model(**hit['_source']) for hit in search_result['hits']['hits']]
            await self.cache.set_by_elastic_query(query, items)
        return items

    async def _get_list_from_elastic(self, ids: List[str]) -> List:
        try:
            res = await self.elastic.mget(body={'ids': ids}, index=self.index)
        except elasticsearch.exceptions.NotFoundError:
            return []
        return [self.model(**doc['_source']) for doc in res['docs']]

    @staticmethod
    def _get_paginated_query(search: Search, page_number: int, page_size: int) -> dict:
        start = (page_number - 1) * page_size
        return search[start: start + page_size].to_dict()
