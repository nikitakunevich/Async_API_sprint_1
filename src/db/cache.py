
from typing import Any, Optional
from aioredis import Redis
import logging
from models.film import Film, Films

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


    async def __getitem__(self, key: str) -> Any:
        return await self.get(key)


class FilmCache(Cache):
    def __init__(self, redis: Redis, path: str, ttl: int) -> None:
        super().__init__(redis, path=path, expire=ttl)

    def parse_raw_film(self, data: Optional[str]) -> Optional[Film]:
        if not data:
            return None
        return Film.parse_raw(data)

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        key = f'id:{film_id}'
        data = await self.get(key)
        return self.parse_raw_film(data)

    async def set_by_id(self, film_id: str, value: Film) -> None:
        key = f'id:{film_id}'
        await self.set(key=key, value=value.json())

    async def get_by_elastic_query(self, query_elastic: dict) -> Optional[Films]:
        key = f'query:{str(query_elastic)}'
        data = await self.get(key)
        if not data:
            return None
        return Films.parse_raw(data)

    async def set_by_elastic_query(self, query_elastic: dict, values: Films) -> None:
        key = f'query:{str(query_elastic)}'
        await self.set(key=key, value=values.json())
