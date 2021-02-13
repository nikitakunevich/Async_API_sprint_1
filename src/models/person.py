from typing import List

import orjson
from pydantic import BaseModel

from models.utils import orjson_dumps


class Person(BaseModel):
    id: str
    full_name: str
    roles: List[str]
    film_ids: List[str]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps
