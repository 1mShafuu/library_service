from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base


class Reader(Base):
    __tablename__ = "readers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    last_visit = Column(Date)

    address = relationship("Address", back_populates="readers")
    loans = relationship("Loan", back_populates="reader")
