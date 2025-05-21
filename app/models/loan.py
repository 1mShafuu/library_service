from sqlalchemy import Column, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"))
    reader_id = Column(Integer, ForeignKey("readers.id"))
    loan_date = Column(Date)
    expected_return_date = Column(Date)
    return_date = Column(Date)

    book = relationship("Book", back_populates="loans")
    reader = relationship("Reader", back_populates="loans")