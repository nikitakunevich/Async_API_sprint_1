from typing import List, Optional

from models.film import Film
from pydantic import BaseModel

from schemas.genre import Genre
from schemas.person import PersonShort


class FilmShort(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float]


class FilmDetails(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: List[Genre]
    actors: List[PersonShort]
    writers: List[PersonShort]
    directors: List[PersonShort]

    @classmethod
    def from_film(cls, film: Film):
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
