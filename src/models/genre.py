from typing import List

import orjson
from pydantic import BaseModel

from models.utils import orjson_dumps


class Filmwork(BaseModel):
    id: str
    title: str
    imdb_rating: float

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Genre(BaseModel):
    id: str
    name: str
    filmworks: List[Filmwork]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
