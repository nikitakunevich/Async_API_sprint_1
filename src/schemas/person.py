from typing import List

from pydantic import BaseModel


class Person(BaseModel):
    uuid: str
    full_name: str
    role: str
    film_ids: List[str]


class PersonShort(BaseModel):
    uuid: str
    full_name: str
