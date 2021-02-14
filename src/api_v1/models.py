from typing import List, Optional

import orjson
from pydantic import BaseModel

import db.models


def orjson_dumps(v, *, default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class APIModel(BaseModel):
    class Config:
        # Заменяем стандартную работу с json на более быструю
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class Person(APIModel):
    uuid: str
    full_name: str
    roles: List[str]
    film_ids: List[str]

    @classmethod
    def from_db_model(cls, person: db.models.Person):
        return cls(
            uuid=person.id,
            full_name=person.full_name,
            roles=person.roles,
            film_ids=person.film_ids
        )


class PersonShort(APIModel):
    uuid: str
    full_name: str


class Genre(APIModel):
    uuid: str
    name: str


class FilmShort(APIModel):
    uuid: str
    title: str
    imdb_rating: Optional[float]

    @classmethod
    def from_db_model(cls, film: db.models.FilmShort):
        return cls(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating
        )


class GenreDetail(APIModel):
    uuid: str
    name: str
    filmworks: List[FilmShort]

    @classmethod
    def from_db_model(cls, genre: db.models.Genre):
        return cls(
            uuid=genre.id,
            name=genre.name,
            filmworks=[FilmShort.from_db_model(film) for film in genre.filmworks]
        )


class FilmDetails(APIModel):
    uuid: str
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: List[Genre]
    actors: List[PersonShort]
    writers: List[PersonShort]
    directors: List[PersonShort]

    @classmethod
    def from_db_model(cls, film: db.models.Film):
        return cls(
            uuid=film.id,
            title=film.title,
            imdb_rating=film.imdb_rating,
            description=film.description,
            genre=[Genre(uuid=genre.id, name=genre.name) for genre in film.genres],
            actors=[PersonShort(uuid=person.id, full_name=person.name) for person in film.actors],
            writers=[PersonShort(uuid=person.id, full_name=person.name) for person in film.writers],
            directors=[PersonShort(uuid=person.id, full_name=person.name) for person in film.directors]
        )
