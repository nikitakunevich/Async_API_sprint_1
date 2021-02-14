from typing import List, Optional

from aioredis import Redis
from core.config import CACHE_TTL
from db.cache import ModelCache
from db.elastic import AsyncElasticsearch, get_elastic
from db.redis import get_redis
from elasticsearch_dsl.search import Search
from fastapi import Depends
from models.genre import Filmwork, Genre

from services.base import BaseESService


class GenreService(BaseESService):
    model = Genre
    index = 'genres'

    def __init__(self, cache: ModelCache, elastic: AsyncElasticsearch):
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
        query = self._get_paginated_query(s, page_number, page_size)
        genres = await self.cache.get_by_elastic_query(query)
        if not genres:
            result = await self.elastic.search(index=self.index, body=query)
            genres = self._get_genre_from_elastic_response(result)
            await self.cache.set_by_elastic_query(query, genres)
        return genres

    @staticmethod
    def _get_genre_from_elastic_response(response: dict) -> List[Genre]:
        return [
            Genre(
                id=hit['_source']['id'],
                name=hit['_source']['name'],
                filmworks=[
                    Filmwork(
                        id=f['id'],
                        title=f['title'],
                        imdb_rating=f['imdb_rating']
                    ) for f in hit['_source']['filmworks']
                ]
            ) for hit in response['hits']['hits']
        ]


def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(ModelCache(redis, Genre, CACHE_TTL), elastic)
