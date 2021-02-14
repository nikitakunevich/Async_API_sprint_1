from typing import Optional, List

from pydantic import BaseModel

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


class FilmShort(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float]


class Genre(BaseModel):
    id: str
    name: str
    filmworks: List[FilmShort]


class Person(BaseModel):
    id: str
    full_name: str
    roles: List[str]
    film_ids: List[str]
