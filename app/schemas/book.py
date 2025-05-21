from pydantic import BaseModel, constr
from .author import AuthorResponse
from typing import Optional


class BookBase(BaseModel):
    title: str
    genre: str


class BookCreate(BookBase):
    author_name: str


class BookUpdate(BaseModel):
    title: constr(max_length=2)
    genre: Optional[str]
    author_name: Optional[str]


class BookResponse(BaseModel):
    id: int
    title: str
    genre: str
    author: AuthorResponse
    is_available: bool

    class Config:
        from_attributes = True
