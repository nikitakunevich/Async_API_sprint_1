
import json
import logging
from typing import Any, List, Optional, Type

from aioredis import Redis
from pydantic import BaseModel
from pydantic.tools import parse_raw_as

logger = logging.getLogger(__name__)


class Cache:
    def __init__(self, redis: Redis, path: str = '', expire: int = 60 * 5) -> None:
        self._redis = redis
        self._path = path
        self._ttl = expire

    def _get_full_path(self, key: str) -> str:
        if not self._path:
            return key
        return f'{self._path}:{key}'

    async def get(self, key: str) -> Any:
        full_key = self._get_full_path(key)
        data = await self._redis.get(full_key)
        if not data:
            return None
        logger.debug(f"Trying to get from cache {key=}, {data=}")
        return data

    async def set(self, key: str, value: Any) -> None:
        full_key = self._get_full_path(key)
        logger.debug(f"Set cache with {key=}")
        await self._redis.set(full_key, value, expire=self._ttl)


class ModelCache(Cache):
    def __init__(self, redis: Redis, model: Type[BaseModel], ttl: int) -> None:
        self._model = model
        super().__init__(redis, path=model.__name__, expire=ttl)

    def parse_raw_model(self, data: Optional[str]) -> Optional[BaseModel]:
        if not data:
            return None
        return self._model.parse_raw(data)

    async def get_by_id(self, film_id: str) -> Optional[BaseModel]:
        key = f'id:{film_id}'
        data = await self.get(key)
        return self.parse_raw_model(data)

    async def set_by_id(self, film_id: str, value: BaseModel) -> None:
        key = f'id:{film_id}'
        await self.set(key=key, value=value.json())

    async def get_by_elastic_query(self, query_elastic: dict) -> Optional[BaseModel]:
        key = f'query:{str(query_elastic)}'
        data = await self.get(key)
        if not data:
            return None
        return parse_raw_as(List[self._model], data)

    async def set_by_elastic_query(self, query_elastic: dict, values: List[BaseModel]) -> None:
        key = f'query:{str(query_elastic)}'
        await self.set(key=key, value=json.dumps([value.dict() for value in values]))
