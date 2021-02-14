import logging
from abc import ABC

import elasticsearch.exceptions
from elasticsearch import AsyncElasticsearch

from db.cache import ModelCache

logger = logging.getLogger(__name__)


class BaseESService(ABC):
    model = None
    index = None

    def __init__(self, cache: ModelCache, elastic: AsyncElasticsearch):
        self.cache = cache
        self.elastic = elastic

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
