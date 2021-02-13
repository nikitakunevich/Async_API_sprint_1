from typing import Optional, List

import orjson
from pydantic import BaseModel

from models.utils import orjson_dumps

ObjectId = str
ObjectName = str


class IdName(BaseModel):
    id: str
    name: str


class Film(BaseModel):
    id: str
    imdb_rating: Optional[float]
    title: str
    description: Optional[str]

    actors_names: List[str]
    writers_names: List[str]
    directors_names: List[str]
    genres_names: List[str]
    actors: List[IdName]
    writers: List[IdName]
    directors: List[IdName]
    genres: List[IdName]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
