from typing import Optional, List, Dict

import orjson

# Используем pydantic для упрощения работы при перегонке данных из json в объекты
from pydantic import BaseModel

ObjectId = str
ObjectName = str


class Film(BaseModel):
    """Схема для ES документа с фильмами."""
    id: str
    imdb_rating: Optional[float]
    title: str
    description: Optional[str]

    actors_names: List[str]
    writers_names: List[str]
    directors_names: List[str]
    genres_names: List[str]
    actors: List[Dict[ObjectId, ObjectName]]
    writers: List[Dict[ObjectId, ObjectName]]
    directors: List[Dict[ObjectId, ObjectName]]
    genres: List[Dict[ObjectId, ObjectName]]

    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson.dumps
