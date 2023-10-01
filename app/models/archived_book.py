from sqlalchemy import Column, Integer, String
from .base import Base


class ArchivedBook(Base):
    __tablename__ = "archived_books"

    id = Column(Integer, primary_key=True)
    original_book_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    genre = Column(String, nullable=False)
    author_name = Column(String, nullable=False)
