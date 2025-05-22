from sqlalchemy import Column, Integer, Date
from .base import Base


class ArchivedLoan(Base):
    __tablename__ = "archived_loans"

    id = Column(Integer, primary_key=True)
    original_loan_id = Column(Integer, index=True, nullable=False)
    book_id = Column(Integer, nullable=False)
    reader_id = Column(Integer, nullable=False)
    loan_date = Column(Date, nullable=False)
    expected_return_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
