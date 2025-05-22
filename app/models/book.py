from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    genre = Column(String)
    author_id = Column(Integer, ForeignKey("authors.id"))
    is_available = Column(Boolean, default=True)

    author = relationship("Author", back_populates="books")
    loans = relationship("Loan", back_populates="book")