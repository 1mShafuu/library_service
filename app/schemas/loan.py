from datetime import date
from pydantic import BaseModel
from typing import Optional


class LoanBase(BaseModel):
    book_id: int
    reader_id: int


class LoanCreate(LoanBase):
    pass


class LoanResponse(LoanBase):
    id: int
    loan_date: date
    return_date: Optional[date] = None

    class Config:
        from_attributes = True
