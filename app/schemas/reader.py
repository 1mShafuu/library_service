from datetime import date
from pydantic import BaseModel
from typing import Optional
from app.schemas import AddressCreate, AddressResponse


class ReaderBase(BaseModel):
    name: str


class ReaderCreate(ReaderBase):
    address: AddressCreate


class ReaderUpdate(ReaderBase):
    address: AddressCreate


class ReaderResponse(BaseModel):
    id: int
    name: str
    last_visit: Optional[date] = None
    address: AddressResponse

    model_config = {"from_attributes": True}


# Разрешаем forward references
ReaderCreate.model_rebuild()
ReaderUpdate.model_rebuild()
ReaderResponse.model_rebuild()
