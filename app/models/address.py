from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from .base import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    city = Column(String)
    street = Column(String)
    readers = relationship("Reader", back_populates="address")
