from typing import List

from pydantic import BaseModel


class Genre(BaseModel):
    uuid: str
    name: str


class Filmwork(BaseModel):
    id: str
    title: str
    imdb_rating: float


class GenreDetail(BaseModel):
    uuid: str
    name: str
    filmworks: List[Filmwork]
